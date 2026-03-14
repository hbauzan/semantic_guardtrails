from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import numpy as np
import io
import pyarrow as pa
import pandas as pd

from app.core.dependencies import get_embedder, get_storage, get_galaxy_cache, get_context_vault, get_identity_resolver, state
from app.modules.embedder import Embedder
from app.modules.storage import Storage, DBItem
from app.modules.geometry import Geometry
from app.modules.context_vault import ContextVault
from app.modules.identity import IdentityResolver
from app.core.config import settings

router = APIRouter(default_response_class=ORJSONResponse)

# --- Request Models ---
class EmbedRequest(BaseModel):
    text: str

class TokenizeRequest(BaseModel):
    text: str
    include_raw_vector: bool = False

class SimulateRequest(BaseModel):
    text: str

class ArithmeticRequest(BaseModel):
    word_a: str
    word_b: str
    word_c: str
    top_k: int = 5
    filter_cluster_id: Optional[int] = None

class SearchRequest(BaseModel):
    vector: List[float]
    top_k: int = 10
    filter_cluster_id: Optional[int] = None

class DimensionAnalysisRequest(BaseModel):
    dimension_index: int
    top_k: int = 10

class InjectPackRequest(BaseModel):
    name: str
    color: str
    description: str
    terms: Dict[str, str]

class ConfigUpdateRequest(BaseModel):
    firewall_threshold: float

# --- Routes ---

@router.post("/galaxy/config")
async def update_config(request: ConfigUpdateRequest):
    state.firewall_threshold = request.firewall_threshold
    return {"status": "success", "firewall_threshold": state.firewall_threshold}

@router.post("/galaxy/simulate")
async def simulate_query(
    request: SimulateRequest,
    response: Response,
    embedder: Embedder = Depends(get_embedder),
    storage: Storage = Depends(get_storage),
    geometry: Geometry = Depends(lambda: state.geometry)
):
    t0 = time.perf_counter()
    
    # 1. Inference
    vector = embedder.encode(request.text)
    
    # 2. Project to 3D and clip to [0, 300] manifold
    vec_reshaped = vector.reshape(1, -1)
    xyz_raw = geometry.transform(vec_reshaped)
    xyz_clipped = np.clip(xyz_raw[0], 0, 300).tolist()
    
    # 3. Collision Check against Sovereign Clusters
    results = storage.search(vector.tolist(), limit=10)
    
    is_blocked = False
    collided_with = None
    
    for hit in results:
        if hit.get('cluster_id', 0) < 0:  # Sovereign Node
            distance = hit.get('_distance', 0.0)
            if distance < state.firewall_threshold:
                is_blocked = True
                collided_with = hit.get('cluster_label', 'Unknown Pack')
                break
                
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Simulation-Time"] = f"{t_process:.2f}ms"
    
    return {
        "xyz": xyz_clipped,
        "is_blocked": is_blocked,
        "collided_with": collided_with
    }

@router.post("/embed")
async def embed_text(
    request: EmbedRequest, 
    response: Response,
    embedder: Embedder = Depends(get_embedder),
    storage: Storage = Depends(get_storage),
    geometry: Geometry = Depends(lambda: state.geometry), # Access global geometry
    identity_resolver: IdentityResolver = Depends(get_identity_resolver)
):
    # 1. Inference
    t0 = time.perf_counter()
    vector = embedder.encode(request.text)
    t_infer = (time.perf_counter() - t0) * 1000

    # 2. Projection (Geometry)
    vec_reshaped = vector.reshape(1, -1)
    
    t1 = time.perf_counter()
    # If geometry is fitted, project. Else 0.
    xyz_raw = geometry.transform(vec_reshaped)
    t_proj = (time.perf_counter() - t1) * 1000
    
    xyz = xyz_raw[0].tolist()
    
    # 3. Token ID (Galaxy Identity)
    galaxy_id = identity_resolver.get_galaxy_id(request.text)
    token_id = galaxy_id if galaxy_id is not None else 0

    # Telemetry Headers
    response.headers["X-Inference-Time"] = f"{t_infer:.2f}ms"
    response.headers["X-Projection-Time"] = f"{t_proj:.2f}ms"
    
    return {
        "embedding": vector.tolist(), 
        "token_id": token_id,
        "xyz": xyz
    }

@router.post("/tokenize")
async def tokenize_text(
    request: TokenizeRequest, 
    response: Response,
    embedder: Embedder = Depends(get_embedder),
    geometry: Geometry = Depends(lambda: state.geometry),
    identity_resolver: IdentityResolver = Depends(get_identity_resolver)
):
    t0 = time.perf_counter()
    
    # 1. Tokenize (Matches Embedder Logic)
    # The embedder.tokenize method returns a list of objects:
    # [{'token': 'art', 'id': 101, 'vector': [0.1, ...]}, ...]
    tokens = embedder.tokenize(request.text)
    
    if not tokens:
        return {"tokens": []}

    # 2. Extract Vectors for Batch Projection
    # We need to stack all 768d vectors into a single numpy array (N, 768)
    vectors = [t['vector'] for t in tokens]
    vector_matrix = np.stack(vectors) # (N, 768)
    
    # 3. Project to 3D (Geometry)
    t1 = time.perf_counter()
    xyz_matrix = geometry.transform(vector_matrix) # Returns (N, 3)
    
    # Clip to Bounds [0, 300] (Mandatory for Crystal Box visualization)
    xyz_matrix = np.clip(xyz_matrix, 0, 300)
    
    t_proj = (time.perf_counter() - t1) * 1000
    
    # 4. Merge Back
    # We iterate and inject 'xyz', removing 'vector' to save bandwidth
    final_tokens = []
    for i, token_obj in enumerate(tokens):
        # Resolve Galaxy ID
        galaxy_id = identity_resolver.get_galaxy_id(token_obj['token'])
        token_obj['galaxy_id'] = galaxy_id if galaxy_id is not None else -1
        
        # geometry.transform returns numpy array, convert to list
        token_obj['xyz'] = xyz_matrix[i].tolist()
        
        # Remove heavy 768d/1024d vector unless explicitly requested
        if 'vector' in token_obj and not request.include_raw_vector:
            del token_obj['vector']
            
        final_tokens.append(token_obj)
        
    t_infer = (time.perf_counter() - t0) * 1000
    
    response.headers["X-Inference-Time"] = f"{t_infer:.2f}ms"
    response.headers["X-Projection-Time"] = f"{t_proj:.2f}ms"
    
    return {"tokens": final_tokens}

@router.post("/arithmetic")
async def arithmetic(
    request: ArithmeticRequest, 
    response: Response,
    embedder: Embedder = Depends(get_embedder),
    storage: Storage = Depends(get_storage),
    geometry: Geometry = Depends(lambda: state.geometry)
):
    # 1. Inference
    t0 = time.perf_counter()
    vectors = embedder.encode([request.word_a, request.word_b, request.word_c])
    t_infer = (time.perf_counter() - t0) * 1000
    
    vec_a, vec_b, vec_c = vectors[0], vectors[1], vectors[2]
    result_vector = vec_a - vec_b + vec_c
    
    # 2. I/O (Search)
    search_vec = result_vector.tolist()
    
    t1 = time.perf_counter()
    results = storage.search(search_vec, limit=request.top_k, filter_cluster_id=request.filter_cluster_id)
    t_io = (time.perf_counter() - t1) * 1000
    
    # Filter results
    input_words = {request.word_a.lower(), request.word_b.lower(), request.word_c.lower()}
    final_results = []
    
    for hit in results:
        word = hit['text']
        if word.lower() not in input_words:
            final_results.append({
                "word": word,
                "score": 1.0 / (1.0 + hit['_distance']),
                "token_id": hit['id'],
                "vector": hit.get('vector', []),
                "_distance": hit['_distance']
            })
            if len(final_results) >= request.top_k:
                break
    
    # 3. Projection of Result (Optional but useful)
    t2 = time.perf_counter()
    # We can try to project the result vector to give it a coordinate?
    try:
        if geometry.is_fitted:
            _ = geometry.transform(result_vector.reshape(1, -1)) # Just compute to measure time
    except:
        pass
    t_proj = (time.perf_counter() - t2) * 1000

    response.headers["X-Inference-Time"] = f"{t_infer:.2f}ms"
    response.headers["X-IO-Time"] = f"{t_io:.2f}ms"
    response.headers["X-Projection-Time"] = f"{t_proj:.2f}ms"

    return {
        "vector": result_vector.tolist(),
        "results": final_results
    }

@router.post("/analyze_dimension")
async def analyze_dimension(
    request: DimensionAnalysisRequest,
    response: Response,
    df: pd.DataFrame = Depends(get_galaxy_cache)
):
    """
    Semantic Probe: Identifies which words activate a specific vector dimension.
    """
    t0 = time.perf_counter()
    
    dim_idx = request.dimension_index
    
    # Validation
    # Assuming vector column is named 'vector' and is a numpy array or list
    if df.empty:
         return {"error": "Galaxy is empty. Please run ingest_vocab.py"}
    
    # We need to extract the specific column from the vector lists
    # This is a bit heavy if done purely in pandas with apply, but for 10k it's fast enough (<50ms)
    # Optimization: Stack vectors into a numpy matrix if not already
    
    # Check if we have a cached numpy matrix for speed
    if not hasattr(state, 'galaxy_matrix'):
        # Create a matrix from the dataframe column 'vector'
        # vector column contains list of floats. We need to stack them.
        state.galaxy_matrix = np.stack(df['vector'].values)
        state.galaxy_text = df['text'].values
        state.galaxy_ids = df['id'].values
    
    # Bounds check
    if dim_idx < 0 or dim_idx >= state.galaxy_matrix.shape[1]:
        return {"error": f"Dimension {dim_idx} out of bounds (Max: {state.galaxy_matrix.shape[1]-1})"}

    # Slicing the column
    column_values = state.galaxy_matrix[:, dim_idx]
    
    # Get Top K indices (Positive)
    # argpartition is faster than argsort for just top k
    if len(column_values) > request.top_k:
        top_indices = np.argpartition(column_values, -request.top_k)[-request.top_k:]
        # Sort the top k specifically
        top_indices = top_indices[np.argsort(column_values[top_indices])][::-1]
        
        # Get Bottom K indices (Negative)
        bottom_indices = np.argpartition(column_values, request.top_k)[:request.top_k]
        bottom_indices = bottom_indices[np.argsort(column_values[bottom_indices])]
    else:
        # If dataset is smaller than top_k, just sort all
        top_indices = np.argsort(column_values)[::-1]
        bottom_indices = np.argsort(column_values)

    # Construct Result
    pos_activators = [
        {"word": state.galaxy_text[i], "value": float(column_values[i]), "id": int(state.galaxy_ids[i])} 
        for i in top_indices
    ]
    
    neg_activators = [
        {"word": state.galaxy_text[i], "value": float(column_values[i]), "id": int(state.galaxy_ids[i])} 
        for i in bottom_indices
    ]
    
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Analysis-Time"] = f"{t_process:.2f}ms"

    return {
        "dimension": dim_idx,
        "label": f"{pos_activators[0]['word']} <-> {neg_activators[0]['word']}",
        "top_activators": pos_activators,
        "bottom_activators": neg_activators
    }

@router.get("/galaxy")
async def galaxy_view(
    response: Response,
    lod: int = 3,
    storage: Storage = Depends(get_storage)
):
    t0 = time.perf_counter()
    df = storage.get_all_vectors()
    
    if df.empty:
        return []

    # Filter based on LOD
    # LOD 1: Top 5% using lod_score (Strategic)
    # LOD 2: Top 25% (Balanced)
    # LOD 3: 100% (Full)
    
    # 1. Segregate Priority IDs (Knowledge Tokens)
    PRIORITY_IDS = [9578, 9579, 9580, 9581, 9582, 9583]
    priority_mask = df['id'].isin(PRIORITY_IDS)
    priority_df = df[priority_mask]
    standard_df = df[~priority_mask]

    # 2. Apply LOD to Standard Tokens Only
    if 'lod_score' not in standard_df.columns:
        standard_df['lod_score'] = 0.0

    if lod < 3:
        standard_df = standard_df.sort_values(by='lod_score', ascending=False)
        total = len(standard_df)
        if lod == 1:
            limit = int(total * 0.05)
        elif lod == 2:
            limit = int(total * 0.25)
        else:
            limit = total
        
        limit = max(limit, 100)
        standard_df = standard_df.head(limit)

    # 3. Merge (Priority on Top)
    df = pd.concat([priority_df, standard_df])

    t_io = (time.perf_counter() - t0) * 1000
    
    if 'xyz' in df.columns:
        # Ensure xyz is list
        df['xyz'] = df['xyz'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    # Columns to return
    if 'lod_score' not in df.columns:
        df['lod_score'] = 0.0
        
    cols =['id', 'xyz', 'text', 'lod_score']
    if 'cluster_id' in df.columns:
        cols.append('cluster_id')
    if 'cluster_label' in df.columns:
        cols.append('cluster_label')
    if 'doc_id' in df.columns:
        cols.append('doc_id')

    records = df[cols].to_dict(orient='records')
    
    response.headers["X-IO-Time"] = f"{t_io:.2f}ms"
    response.headers["X-Total-Points"] = str(len(records))
    
    return records

@router.get("/galaxy/stream")
async def galaxy_stream(
    response: Response,
    lod: int = 3,
    storage: Storage = Depends(get_storage)
):
    t0 = time.perf_counter()
    df = storage.get_all_vectors()
    
    if df.empty:
        headers = {
            "X-Payload-Format": "arrow",
            "X-Total-Points": "0",
            "X-Process-Time": "0.00ms"
        }
        return Response(content=b"", media_type="application/vnd.apache.arrow.stream", headers=headers)
    # Filter based on LOD
    # 1. Segregate Priority IDs (Knowledge Tokens)
    PRIORITY_IDS = [9578, 9579, 9580, 9581, 9582, 9583]
    priority_mask = df['id'].isin(PRIORITY_IDS)
    priority_df = df[priority_mask]
    standard_df = df[~priority_mask]

    # 2. Apply LOD to Standard Tokens Only
    if 'lod_score' in standard_df.columns and lod < 3:
        standard_df = standard_df.sort_values(by='lod_score', ascending=False)
        total = len(standard_df)
        if lod == 1:
            limit = int(total * 0.05)
        elif lod == 2:
            limit = int(total * 0.25)
        else:
            limit = total
        limit = max(limit, 100)
        standard_df = standard_df.head(limit)

    # 3. Merge (Priority on Top)
    df = pd.concat([priority_df, standard_df])

    # Convert to Arrow Table
    if 'lod_score' not in df.columns:
        df['lod_score'] = 0.0
        
    cols =['id', 'xyz', 'text', 'lod_score']
    if 'cluster_id' in df.columns: cols.append('cluster_id')
    if 'cluster_label' in df.columns: cols.append('cluster_label')
    if 'doc_id' in df.columns: cols.append('doc_id')
    
    df_filtered = df[cols].copy()
    
    table = pa.Table.from_pandas(df_filtered)
    
    # Serialize to IPC Stream
    sink = io.BytesIO()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
        
    arrow_bytes = sink.getvalue()
    
    t_process = (time.perf_counter() - t0) * 1000
    
    headers = {
        "X-Payload-Format": "arrow",
        "X-Total-Points": str(len(df_filtered)),
        "X-Process-Time": f"{t_process:.2f}ms"
    }
    
    return Response(content=arrow_bytes, media_type="application/vnd.apache.arrow.stream", headers=headers)

@router.post("/search")
async def search(
    request: SearchRequest,
    response: Response,
    storage: Storage = Depends(get_storage)
):
    t0 = time.perf_counter()
    
    results = storage.search(
        query_vector=request.vector, 
        limit=request.top_k, 
        filter_cluster_id=request.filter_cluster_id
    )
    
    t_io = (time.perf_counter() - t0) * 1000
    response.headers["X-IO-Time"] = f"{t_io:.2f}ms"
    
    return results

@router.get("/clusters/summary")
async def cluster_summary(
    response: Response,
    storage: Storage = Depends(get_storage)
):
    """
    Returns a lightweight list of all islands (clusters).
    Format: [{"id": 1, "label": "medical", "count": 45, "centroid_xyz": [x,y,z]}, ...]
    """
    t0 = time.perf_counter()
    df = storage.get_all_vectors()
    
    if df.empty or 'cluster_id' not in df.columns:
        return []

    # Include GALAXY_BASE (-1) in summary
    clusters = df
    
    if clusters.empty:
        return []

    # Group by cluster_id and label
    summary = []
    grouped = clusters.groupby(['cluster_id', 'cluster_label'])
    
    for (cid, label), group in grouped:
        # Calculate centroid of XYZ
        xyz_values = group['xyz'].values
        # Filter out Nones if any
        valid_xyz = [x for x in xyz_values if x is not None and len(x) == 3]
        
        if valid_xyz:
            centroid_xyz = np.mean(np.stack(valid_xyz), axis=0).tolist()
        else:
            centroid_xyz = [0.0, 0.0, 0.0]
            
        summary.append({
            "id": int(cid),
            "label": str(label),
            "count": int(len(group)),
            "centroid_xyz": centroid_xyz
        })
        
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Process-Time"] = f"{t_process:.2f}ms"
    
    # Sort by count desc
    summary.sort(key=lambda x: x['count'], reverse=True)
    
    return summary

@router.get("/debug/fidelity")
async def debug_fidelity(geometry: Geometry = Depends(lambda: state.geometry)):
    if not geometry.is_fitted:
        return {"error": "Geometry not fitted"}
    
    # Generate random test vectors (Simulating VECTOR_DIM embeddings)
    test_vectors = np.random.rand(50, settings.VECTOR_DIM).astype(np.float32)
    # Normalize
    norms = np.linalg.norm(test_vectors, axis=1, keepdims=True)
    test_vectors = test_vectors / norms
    
    # 1. Ground Truth (Teacher)
    truth_raw = geometry.reducer.transform(test_vectors)
    
    # 2. Shadow Prediction (Student)
    pred_raw = geometry.shadow_projector.predict(test_vectors)
    
    # 3. MSE
    mse = np.mean((truth_raw - pred_raw) ** 2)
    
    return {
        "mse": float(mse),
        "status": "PASS" if mse < 10.0 else "FAIL", 
        "note": "Comparing Raw UMAP vs MLP output"
    }

@router.get("/inspect/{token_id}")
async def inspect_token(
    token_id: int,
    response: Response,
    storage: Storage = Depends(get_storage),
    context_vault: ContextVault = Depends(get_context_vault)
):
    """
    Hybrid Lookup: Metadata (LanceDB) + Context (SQLite)
    """
    t0 = time.perf_counter()
    
    # 1. Vector Vault Lookup (LanceDB)
    df = storage.get_all_vectors()
    item = df[df['id'] == token_id]
    
    if item.empty:
        raise HTTPException(status_code=404, detail=f"Token ID {token_id} not found in Galaxy.")
    
    record = item.iloc[0].to_dict()
    
    # Cleanup numpy types
    if 'xyz' in record and isinstance(record['xyz'], np.ndarray):
        record['xyz'] = record['xyz'].tolist()
    if 'vector' in record and isinstance(record['vector'], np.ndarray):
        record['vector'] = record['vector'].tolist()
        
    # 2. Context Vault Lookup (SQLite)
    context_data = context_vault.get_context(token_id)
    
    # 3. Merge
    record['context'] = context_data
    
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Process-Time"] = f"{t_process:.2f}ms"
    
    return record


@router.post("/corpus/inject-pack")
async def inject_pack(
    request: InjectPackRequest,
    response: Response,
    embedder: Embedder = Depends(get_embedder),
    storage: Storage = Depends(get_storage),
    geometry: Geometry = Depends(lambda: state.geometry),
    context_vault: ContextVault = Depends(get_context_vault),
    identity_resolver: IdentityResolver = Depends(get_identity_resolver)
):
    t0 = time.perf_counter()
    
    # 1. Register Dictionary
    dict_id = context_vault.create_dictionary(request.name, request.color, request.description)
    dynamic_cluster_id = -(dict_id * 10)
    
    # 2. Find Starting ID for new terms
    df = storage.get_all_vectors()
    if not df.empty and 'id' in df.columns:
        sov_ids = df[df['id'] >= 10000]['id'].tolist()
        next_new_id = max(sov_ids) + 1 if sov_ids else 10000
    else:
        next_new_id = 10000
        
    new_items_to_add = []
    existing_ids_to_update = []
    
    print(f"📦 Injecting Sovereign Pack: {request.name} ({len(request.terms)} terms)")
    
    # 3. Process terms
    for term, definition in request.terms.items():
        term = term.strip()
        if not term:
            continue
            
        galaxy_id = identity_resolver.get_galaxy_id(term)
        
        if galaxy_id is not None:
            # Term exists (base vocabulary or previous inject)
            existing_ids_to_update.append(galaxy_id)
            context_vault.add_definition(galaxy_id, request.name, definition, weight=1.5)
        else:
            # New Term
            vector = embedder.encode(term)
            # Project and clip
            xyz_raw = geometry.transform(vector.reshape(1, -1))
            xyz_clipped = np.clip(xyz_raw[0], 0, 300).tolist()
            
            # Create DBItem
            item = DBItem(
                id=next_new_id,
                text=term,
                vector=vector.tolist(),
                xyz=xyz_clipped,
                metadata={"source": request.name},
                cluster_id=dynamic_cluster_id,
                cluster_label=request.name.strip("'\""),
                lod_score=1.0
            )
            new_items_to_add.append(item)
            
            # Save mapping in memory BEFORE batch add to avoid race conditions
            identity_resolver.galaxy_map[term] = next_new_id
            
            # Add def to sqlite
            context_vault.add_definition(next_new_id, request.name, definition, weight=1.5)
            
            next_new_id += 1
            
    # 4. Batch Operations
    if new_items_to_add:
        storage.add(new_items_to_add)
        
    if existing_ids_to_update:
        storage.update_clusters(
            ids=existing_ids_to_update,
            cluster_ids=[dynamic_cluster_id] * len(existing_ids_to_update),
            labels=[request.name.strip("'\"")] * len(existing_ids_to_update)
        )
        
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Injection-Time"] = f"{t_process:.2f}ms"
    
    return {
        "status": "success",
        "pack": request.name,
        "new_terms": len(new_items_to_add),
        "existing_updates": len(existing_ids_to_update)
    }

@router.delete("/corpus/remove-pack/{label}")
async def remove_pack(
    label: str,
    response: Response,
    storage: Storage = Depends(get_storage),
    context_vault: ContextVault = Depends(get_context_vault),
    identity_resolver: IdentityResolver = Depends(get_identity_resolver)
):
    t0 = time.perf_counter()
    label = label.strip("'\"")
    
    # 1. Remove from SQLite (CASCADE takes care of definitions)
    context_vault.delete_dictionary(label)
    
    # 2. Get affected LanceDB nodes
    df = storage.get_all_vectors()
    if df.empty or 'cluster_label' not in df.columns:
        return {"status": "success", "deleted": 0, "reset": 0}
        
    affected_nodes = df[df['cluster_label'] == label]
    if affected_nodes.empty:
        return {"status": "success", "deleted": 0, "reset": 0}
        
    hard_delete_ids = affected_nodes[affected_nodes['id'] >= 10000]['id'].tolist()
    reset_ids = affected_nodes[affected_nodes['id'] < 10000]['id'].tolist()
    
    # 3. Hard Delete (Sovereign Ingestions)
    if hard_delete_ids:
        storage.delete(hard_delete_ids)
        # Remove from IdentityResolver memory map!
        terms_to_remove = affected_nodes[affected_nodes['id'] >= 10000]['text'].tolist()
        for t in terms_to_remove:
            if t in identity_resolver.galaxy_map:
                del identity_resolver.galaxy_map[t]
                
    # 4. Reset (Base Vocabulary Nodes that were highjacked by the pack)
    if reset_ids:
        storage.update_clusters(
            ids=reset_ids,
            cluster_ids=[-1] * len(reset_ids),
            labels=["GALAXY_BASE"] * len(reset_ids)
        )
        
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Deletion-Time"] = f"{t_process:.2f}ms"
    
    return {
        "status": "success",
        "pack": label,
        "deleted": len(hard_delete_ids),
        "reset": len(reset_ids)
    }

@router.get("/corpus/neighbors/{node_id}")
async def get_node_neighbors(
    node_id: int,
    response: Response,
    limit: int = 5,
    storage: Storage = Depends(get_storage)
):
    t0 = time.perf_counter()
    neighbors = storage.get_nearest_neighbors(node_id, k=limit)
    
    t_process = (time.perf_counter() - t0) * 1000
    response.headers["X-Neighbor-Search-Time"] = f"{t_process:.2f}ms"
    
    return {
        "node_id": node_id,
        "neighbors": neighbors
    }
