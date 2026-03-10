import subprocess
import sys
import time
import os
from pathlib import Path

# Define paths
BACKEND_DIR = Path(__file__).parent.resolve()
PYTHON_EXE = sys.executable

# Add backend directory to sys.path to allow importing app.core.config
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.modules.storage import Storage
import lancedb

def run_step(script_name, description):
    script_path = BACKEND_DIR / script_name
    print(f"\n⚙️  [STEP] {description} ({script_name})...")
    try:
        t0 = time.time()
        subprocess.run([PYTHON_EXE, str(script_path)], check=True)
        print(f"✅ [PASS] Completed in {time.time() - t0:.2f}s")
    except subprocess.CalledProcessError:
        print(f"❌ [FAIL] {script_name} encountered an error.")
        sys.exit(1)

def check_system_state():
    print(f"🔍 Checking CrystalVault for Model: {settings.MODEL_NAME} ({settings.VECTOR_DIM}D)")
    
    EXPECTED_TABLE_NAME = f"vectors_{settings.MODEL_NAME.replace('/', '_').replace('-', '_').replace(' ', '_')}_{settings.VECTOR_DIM}"
    
    # Check for legacy tables
    legacy_found = False
    uri = str(settings.LANCEDB_URI)
    if os.path.exists(uri):
        try:
            db = lancedb.connect(uri)
            for table_name in db.table_names():
                if table_name.startswith("vectors_") and table_name != EXPECTED_TABLE_NAME:
                    legacy_found = True
                    print(f"⚠️  Legacy model table detected: {table_name}")
                    break
        except Exception as e:
            print(f"⚠️  Failed to inspect LanceDB tables: {e}")
    
    # Instantiate storage which will create the expected table if it doesn't exist
    storage = Storage(model_name=settings.MODEL_NAME, dimension=settings.VECTOR_DIM)
    
    count = storage.total_items
    
    if count == 0:
        if legacy_found:
            print("🚨 Dimension/Model mismatch detected. Triggering deep clean...")
            wipe_script = BACKEND_DIR / "scripts" / "wipe_engine.py"
            subprocess.run([PYTHON_EXE, str(wipe_script), "--all", "--force"], check=True)
            print("✅ Clean slate achieved. Proceeding to hydrate new model space.")
            return True # Needs hydration
        else:
            print("🔰 Empty Vault detected. System requires initial hydration.")
            return True # Needs hydration
    else:
        print(f"✅ System Nominal: Found {count} items in Vault. Bypassing ingestion protocol.")
        return False # Does not need hydration

def main():
    print("==========================================")
    print("      CRYSTAL BOX CALIBRATION TOOL        ")
    print("==========================================")
    
    needs_sync = check_system_state()
    
    if needs_sync:
        # 1. Ingest Vocab (Embed + UMAP + MLP Train)
        run_step("ingest_vocab.py", "Training Geometry & Shadow Projector")
        
        # 2. Process Clusters (HDBSCAN + LOD)
        run_step("process_clusters.py", "Calculating Semantic Islands & LOD")
        
        import shutil
        import glob
        
        demo_src_dir = BACKEND_DIR.parent / "demo_dictionaries"
        dict_dest_dir = BACKEND_DIR / "data" / "dictionaries"
        dict_dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear the destination directory of json files first
        for f in glob.glob(str(dict_dest_dir / "*.json")):
            os.remove(f)
            
        if settings.LOAD_DEMOS:
            print("📦 Ingesting Demo Dictionaries based on configuration...")
            for f in glob.glob(str(demo_src_dir / "*.json")):
                shutil.copy(f, dict_dest_dir)
        else:
            print("🈳 Skipping Demo Dictionaries (LOAD_DEMOS=False).")
            
        # 3. Ingest Dictionaries (Context Linking)
        run_step("ingest_dictionaries.py", "Injecting Knowledge Definitions")
        
        print("\n✨ SYSTEM CALIBRATED. READY FOR VISUALIZATION.")
    else:
        print("\n✨ AUTONOMIC BYPASS: No recalibration required.")

if __name__ == "__main__":
    main()
