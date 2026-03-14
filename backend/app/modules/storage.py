import lancedb
import pyarrow as pa
import pandas as pd
from typing import List, Optional, Dict, Any
from app.core.config import settings
from pydantic import BaseModel, field_validator
import json

class DBItem(BaseModel):
    vector: List[float]
    text: str
    metadata: Dict[str, Any]
    id: Optional[int] = None
    xyz: Optional[List[float]] = None
    cluster_id: Optional[int] = -1
    cluster_label: Optional[str] = "GALAXY_BASE"
    lod_score: Optional[float] = 0.0
    doc_id: Optional[str] = ""

    @field_validator('cluster_label', mode='before')
    @classmethod
    def strip_quotes(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip("'").strip('"')
        return v

class Storage:
    def __init__(self, model_name: str, dimension: int, table_name: Optional[str] = None):
        self.uri = str(settings.LANCEDB_URI)
        self.db = lancedb.connect(self.uri)
        
        if table_name:
            self.table_name = table_name
        else:
            # Dynamic Table Name: vectors_all_mpnet_base_v2_768
            safe_name = model_name.replace("/", "_").replace("-", "_").replace(" ", "_")
            self.table_name = f"vectors_{safe_name}_{dimension}"
        self.dimension = dimension
        
        self._init_table()

    def _init_table(self):
        # Schema definition
        schema = pa.schema([
            pa.field("vector", pa.list_(pa.float32(), self.dimension)),
            pa.field("text", pa.string()),
            pa.field("metadata", pa.string()), # JSON string
            pa.field("xyz", pa.list_(pa.float32(), 3)),
            pa.field("id", pa.int64()),
            pa.field("cluster_id", pa.int32()),
            pa.field("cluster_label", pa.string()),
            pa.field("lod_score", pa.float32()),
            pa.field("doc_id", pa.string())
        ])
        
        if self.table_name not in self.db.table_names():
            print(f"📦 Creating new Crystal Vault: {self.table_name}")
            self.db.create_table(self.table_name, schema=schema)
        else:
            print(f"📂 Connected to Vault: {self.table_name}")
        
        self.table = self.db.open_table(self.table_name)

    def add(self, items: List[DBItem]):
        data = []
        for item in items:
            row = {
                "vector": item.vector,
                "text": item.text,
                "metadata": json.dumps(item.metadata),
                "xyz": item.xyz if item.xyz else [0.0, 0.0, 0.0],
                "id": item.id if item.id is not None else 0,
                "cluster_id": item.cluster_id if item.cluster_id is not None else -1,
                "cluster_label": item.cluster_label if item.cluster_label else "GALAXY_BASE",
                "lod_score": item.lod_score if item.lod_score is not None else 0.0,
                "doc_id": item.doc_id if item.doc_id else ""
            }
            data.append(row)
        
        # Upsert Logic: Delete existing IDs then insert
        ids_to_process = [item.id for item in items if item.id is not None]
        if ids_to_process:
            self.delete(ids_to_process)

        self.table.add(data)

    def search(self, query_vector: List[float], limit: int = 10, filter_cluster_id: Optional[int] = None) -> List[Dict]:
        # LanceDB search
        query = self.table.search(query_vector, vector_column_name="vector").metric("l2")
        
        if filter_cluster_id is not None:
            query = query.where(f"cluster_id = {filter_cluster_id}")
            
        results = query.limit(limit).to_pandas()
        
        # Ensure numpy arrays are converted to lists for JSON serialization
        if 'vector' in results.columns:
            results['vector'] = results['vector'].apply(lambda x: x.tolist() if hasattr(x, 'tolist') else x)
        if 'xyz' in results.columns:
            results['xyz'] = results['xyz'].apply(lambda x: x.tolist() if hasattr(x, 'tolist') else x)
            
        return results.to_dict(orient="records")

    def get_nearest_neighbors(self, item_id: int, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Fetch the target vector by querying the table for item_id
        df = self.table.to_pandas()
        target_row = df[df['id'] == item_id]
        
        # 2. If not found, return an empty list []
        if target_row.empty:
            return []
            
        # 3. Extract the vector as a 1D list/array
        target_vector = target_row.iloc[0]['vector']
        if hasattr(target_vector, 'tolist'):
            target_vector = target_vector.tolist()
            
        # 4. Execute a cosine search
        results = self.table.search(target_vector, vector_column_name="vector").limit(k + 1).to_pandas()
        
        # 5. Filter out the original item_id and map to dicts
        neighbors = []
        for _, row in results.iterrows():
            nid = int(row['id'])
            if nid != item_id:
                # _distance from LanceDB is now L2 distance
                # We map to a similarity score using decay function: 1.0 / (1.0 + distance)
                dist = float(row.get('_distance', 0.0))
                # Map L2 to score
                score = 1.0 / (1.0 + dist)
                
                neighbors.append({
                    "id": nid,
                    "score": round(score, 4)
                })
                if len(neighbors) == k:
                    break
                    
        return neighbors

    def delete(self, ids: List[int]):
        """Removes items from the vault by ID."""
        if not ids:
            return
        # LanceDB SQL-style deletion
        # escape or validate ids to prevent injection if they weren't ints, but type hint says ints.
        id_str = ", ".join(map(str, ids))
        self.table.delete(f"id IN ({id_str})")
    
    def get_all_vectors(self) -> pd.DataFrame:
        self.table = self.db.open_table(self.table_name)
        return self.table.to_pandas()

    def update_xyz(self, ids: List[int], xyz_data: List[List[float]]):
        """Updates XYZ using merge."""
        df = pd.DataFrame({
            "id": ids,
            "xyz": xyz_data
        })
        # Merge on ID to update XYZ column
        self.table.merge(df, on="id")

    @property
    def total_items(self) -> int:
        return len(self.table)
    
    def update_clusters(self, ids: List[int], cluster_ids: List[int], labels: List[str]):
        """Updates cluster info using update mapping."""
        for id_, cid, lbl in zip(ids, cluster_ids, labels):
            safe_lbl = lbl.strip("'").strip('"').replace("'", "''") 
            self.table.update(where=f"id = {id_}", values={"cluster_id": str(cid), "cluster_label": safe_lbl})

    def update_lod_scores(self, ids: List[int], scores: List[float]):
        """Updates lod_score using merge."""
        df = pd.DataFrame({
            "id": ids,
            "lod_score": scores
        })
        self.table.merge(df, on="id")
