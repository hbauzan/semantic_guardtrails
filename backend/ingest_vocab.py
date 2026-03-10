import sys
import time
from pathlib import Path
from tqdm import tqdm
import numpy as np

# Add backend to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent))

from app.core.config import settings
from app.core.dependencies import get_embedder, get_storage, state
from app.modules.storage import DBItem
from app.modules.geometry import Geometry

def ingest_galaxy():
    print("🌌 Initializing Galaxy Ingestion Protocol...")
    
    # 1. Load Resources
    embedder = get_embedder()
    # Force load geometry to ensure we have the object, but we will re-fit it.
    geometry = Geometry() 
    storage = get_storage()
    
    vocab_path = settings.VOCAB_PATH
    if not vocab_path.exists():
        print(f"❌ Vocab file not found: {vocab_path}")
        sys.exit(1)

    # 2. Read Vocab
    print(f"📖 Reading vocabulary from {vocab_path}...")
    with open(vocab_path, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    
    print(f"✨ Found {len(words)} tokens. Starting Batch Embedding...")

    # 3. Batch Embedding
    batch_size = 100
    all_vectors = []
    all_items = []
    
    # We process in chunks to show progress and manage RAM
    import gc
    for i in tqdm(range(0, len(words), batch_size), desc="Embedding"):
        batch_words = words[i : i + batch_size]
        
        # Enforce Dimension
        assert settings.VECTOR_DIM == 1024, f"Vector dimension mismatch. Expected 1024, got {settings.VECTOR_DIM}. Neural core misaligned."
        
        # Encode
        vectors = embedder.encode(batch_words)
        
        # Store temporarily
        for j, word in enumerate(batch_words):
            galaxy_id = i + j
            if galaxy_id > 8999:
                raise RuntimeError("Vocabulary Capacity Exhausted: ID space [0-8999] exceeded. DMZ breach prevented.")
            all_vectors.append(vectors[j])
            all_items.append(DBItem(
                text=word,
                vector=vectors[j].tolist(),
                metadata={"source": "vocab_galaxy"},
                id=galaxy_id  # Simple integer ID for the galaxy
            ))
        
        # Free memory at each batch step
        gc.collect()

    # Convert to numpy for Geometry
    matrix = np.array(all_vectors)
    
    # 4. Fit the Manifold (The Crystal Box)
    print("📐 Fitting 3D Manifold (UMAP + Scaling)... this may take a moment.")
    t0 = time.time()
    # This trains UMAP on the whole dataset and saves the state
    xyz_matrix = geometry.fit_transform(matrix)
    print(f"✅ Manifold fitted in {time.time() - t0:.2f}s")

    # 5. Assign Coordinates & Persist
    print("💾 Persisting to Crystal Vault (LanceDB)...")
    final_items = []
    for idx, item in enumerate(all_items):
        item.xyz = xyz_matrix[idx].tolist()
        final_items.append(item)
        
    # Batch insert to LanceDB
    # We can insert all at once or in chunks. LanceDB handles large inserts well.
    storage.add(final_items)
    
    print(f"🚀 Galaxy Ingestion Complete. {len(final_items)} stars mapped.")
    print(f"📂 Geometry State saved to: {geometry.model_path}")

if __name__ == "__main__":
    ingest_galaxy()
