import umap
import numpy as np
import joblib
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import HDBSCAN
from typing import Tuple
from app.core.config import settings
import time

class Geometry:
    def __init__(self, model_path: Path = None):
        if model_path is None:
            self.model_path = settings.BASE_DIR.resolve() / "data" / "geometry_state.pkl"
        else:
            self.model_path = model_path.resolve()
        # UMAP: The Teacher (Ground Truth Generator)
        self.reducer = umap.UMAP(n_components=3, random_state=42, n_neighbors=15, min_dist=0.1)
        # MLP: The Student (Shadow Projector for Real-Time Inference)
        self.shadow_projector = MLPRegressor(
            hidden_layer_sizes=(256, 128),
            activation='relu',
            solver='adam',
            random_state=42,
            max_iter=500
        )
        # Scaler: Normalizes to Unit Cube [0, 300]
        self.scaler = MinMaxScaler(feature_range=(0, 300))
        self.is_fitted = False
        
        self._load()

    def fit_transform(self, vectors: np.ndarray) -> np.ndarray:
        """
        1. Learn Manifold (UMAP).
        2. Train Shadow Projector (MLP) to mimic UMAP.
        3. Learn Bounds (Scaler).
        """
        print(f"📐 Computing Manifold (Teacher) for {len(vectors)} points...")
        t0 = time.time()
        
        # 1. Generate Ground Truth via UMAP
        raw_3d = self.reducer.fit_transform(vectors)
        print(f"   - UMAP finished in {time.time() - t0:.2f}s")
        
        # 2. Train Shadow Projector
        print("🧠 Training Shadow Projector (Student)...")
        t1 = time.time()
        self.shadow_projector.fit(vectors, raw_3d)
        print(f"   - MLP trained in {time.time() - t1:.2f}s")
        
        # 3. Normalize
        norm_3d = self.scaler.fit_transform(raw_3d)
        
        self.is_fitted = True
        self._save()
        return norm_3d

    def transform(self, vectors: np.ndarray) -> np.ndarray:
        """
        High-Speed Projection using the Shadow Projector (MLP).
        Latency Target: <10ms
        """
        if not self.is_fitted:
            # Fallback to origin to prevent crash
            return np.zeros((len(vectors), 3))
            
        # 1. Predict Raw 3D (Fast Inference)
        raw_3d = self.shadow_projector.predict(vectors)
        
        # 2. Normalize
        norm_3d = self.scaler.transform(raw_3d)
        
        # Singularity Detection
        for i in range(len(norm_3d)):
            if np.allclose(norm_3d[i], [0.0, 0.0, 0.0], atol=1e-8):
                norm_3d[i] += np.random.uniform(-1e-5, 1e-5, size=3)
                
        return norm_3d

    def compute_clusters(self, vectors: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Unsupervised Semantic Clustering using HDBSCAN.
        Input: High-dimensional vectors (768D), NOT 3D projection.
        Output: labels (-1 for noise), probabilities
        """
        print(f"🧩 Computing Clauses (HDBSCAN) for {len(vectors)} points...")
        t0 = time.time()
        
        # metric='euclidean' usually requires normalized vectors for cosine similarity equivalent
        # If vectors are already normalized (which they should be from embedder), euclidean is fine.
        hdb = HDBSCAN(min_cluster_size=15, metric='euclidean')
        cluster_labels = hdb.fit_predict(vectors)
        probs = hdb.probabilities_
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        print(f"   - Found {n_clusters} clusters in {time.time() - t0:.2f}s")
        
        return cluster_labels, probs

    def _save(self):
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                'reducer': self.reducer, 
                'scaler': self.scaler,
                'shadow_projector': self.shadow_projector
            }, self.model_path)
            print(f"💾 Geometry state (Teacher+Student) saved to {self.model_path}")
        except Exception as e:
            print(f"❌ Failed to save geometry state: {e}")

    def _load(self):
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.reducer = data['reducer']
                self.scaler = data['scaler']
                if 'shadow_projector' in data:
                    self.shadow_projector = data['shadow_projector']
                    
                    # Verify Dimension Match for new Core Upgrades (e.g. 768 to 1024)
                    if hasattr(self.shadow_projector, 'n_features_in_') and self.shadow_projector.n_features_in_ != settings.VECTOR_DIM:
                        print("⚠️ Dimension mismatch detected. Geometry requires recalibration.")
                        self.is_fitted = False
                        return

                else:
                    print("⚠️ Legacy Geometry detected. Shadow Projector missing. Please re-ingest galaxy.")
                    self.is_fitted = False # Force re-fit
                    return

                self.is_fitted = True
                print("📂 Geometry state loaded (Shadow Projector Active).")
            except Exception as e:
                print(f"⚠️ Failed to load geometry state: {e}")
                self.is_fitted = False
