import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.storage import Storage, DBItem
from app.modules.context_vault import ContextVault
from app.modules.identity import IdentityResolver
from app.modules.embedder import Embedder
from app.modules.geometry import Geometry
from app.core.config import settings

def ingest_dictionaries():
    print("=== 🧠 Crystal Box: Semantic Injection Protocol ===")
    
    try:
        # Initialize Storage for IdentityResolver
        storage = Storage(model_name=settings.MODEL_NAME, dimension=settings.VECTOR_DIM)
        identity_resolver = IdentityResolver(storage)
        
        context_vault = ContextVault()
        
        embedder = Embedder()
        embedder.load()
        geometry = Geometry()
        
        # 1. Wipe definitions
        context_vault.wipe_definitions()
        
        import glob
        import json
        
        dictionaries = []
        dict_pattern = str(settings.BASE_DIR.resolve() / "data" / "dictionaries" / "*.json")
        for filepath in glob.glob(dict_pattern):
            with open(filepath, 'r', encoding='utf-8') as f:
                dictionaries.append(json.load(f))

        total_processed = 0
        total_linked = 0
        total_sovereign = 0
        next_new_id = 10000
        
        for dictionary in dictionaries:
            dict_name = dictionary["name"]
            dict_color = dictionary["color"]
            dict_desc = dictionary["description"]
            
            print(f"--> 📂 Mounting Dictionary: {dict_name}")
            
            c_id = -1
            try:
                dict_id = context_vault.create_dictionary(dict_name, dict_color, dict_desc)
                c_id = -(dict_id * 10)
            except Exception as e:
                print(f"    ⚠️ Meta Error: {e}")

            for term, definition in dictionary["terms"].items():
                total_processed += 1
                # 1. Resolve Galaxy ID
                galaxy_id = identity_resolver.get_galaxy_id(term)
                
                if galaxy_id is None:
                    galaxy_id = next_new_id
                    next_new_id += 1
                    total_sovereign += 1
                    print(f"    [NEW] Allocating ID {galaxy_id} for '{term}'")
                    
                    vec = embedder.encode(term)
                    vec_2d = vec.reshape(1, -1) if vec.ndim == 1 else vec
                    xyz = geometry.transform(vec_2d)[0]
                    
                    # c_id is already defined above from context_vault
                    item = DBItem(
                        id=galaxy_id,
                        text=term,
                        vector=vec.tolist() if vec.ndim == 1 else vec[0].tolist(),
                        xyz=xyz.tolist(),
                        metadata={"source": dict_name},
                        cluster_id=c_id,
                        cluster_label=dict_name,
                        lod_score=1.0
                    )
                    storage.add([item])
                    print(f"    [LANCEDB] Injected '{term}' at XYZ: {xyz}")
                else:
                    total_linked += 1
                    # [SSA MANDATE] Force existing Galaxy nodes to inherit the Sovereign Dictionary label
                    storage.update_clusters([galaxy_id], [c_id], [dict_name])
                    
                # 2. Inject into Context Vault
                # Weight 1.5 gives these definitions priority in visualization
                context_vault.add_definition(galaxy_id, dict_name, definition, weight=1.5)
                print(f"    [LINKED] '{term}' -> ID {galaxy_id}")

        print(f"=== ✅ Injection Complete ===")
        print(f"   - Total Terms Processed: {total_processed}")
        print(f"   - Total Linked (Existing Galaxy IDs): {total_linked}")
        print(f"   - Total Sovereign Created (IDs >= 10000): {total_sovereign}")

    except Exception as e:
        print(f"❌ Critical Injection Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ingest_dictionaries()
