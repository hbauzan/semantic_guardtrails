from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any, Optional
import numpy as np
import torch
import gc
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# --- Abstract Strategy Interface ---
class EmbedderStrategy(ABC):
    @abstractmethod
    def load(self) -> None:
        """Initialize the underlying model."""
        pass

    @abstractmethod
    def unload(self) -> None:
        """Free resources."""
        pass

    @abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Return raw sentence vectors."""
        pass

    @abstractmethod
    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        """Return contextual token metadata (id, text, vector)."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the model name for storage namespacing."""
        pass

# --- Concrete Strategy: Local HuggingFace ---
class LocalHFStrategy(EmbedderStrategy):
    def __init__(self, model_name: str, device: str):
        self.model_name = model_name
        self.device = device
        self.model: Optional[SentenceTransformer] = None
        self._dim: Optional[int] = None

    def load(self):
        if self.model is None:
            print(f"🔌 Loading Local Model: {self.model_name} on {self.device}...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self._dim = self.model.get_sentence_embedding_dimension()

    def unload(self):
        if self.model is not None:
            print(f"🔌 Unloading Model: {self.model_name}...")
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not loaded. Use 'with embedder:' or call load().")
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        """
        Performs a full forward pass to capture CONTEXTUAL embeddings.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded.")

        # 1. Tokenize
        # We use the internal tokenizer to get inputs
        features = self.model.tokenizer([text], padding=True, truncation=True, return_tensors="pt")
        
        # Move to device
        features = {k: v.to(self.model.device) for k, v in features.items()}

        # 2. Forward Pass (Contextual)
        with torch.no_grad():
            output = self.model.forward(features)
        
        # 3. Extract Token Embeddings (Hidden State)
        # output['token_embeddings'] is [Batch, Seq_Len, Dim]
        token_embeddings = output['token_embeddings'][0].cpu().numpy()
        
        # 4. Map IDs to Tokens
        input_ids = features['input_ids'][0].cpu().tolist()
        tokens = self.model.tokenizer.convert_ids_to_tokens(input_ids)

        # 5. Construct Response
        result = []
        for i, (token, tid, vec) in enumerate(zip(tokens, input_ids, token_embeddings)):
            result.append({
                "token": token,
                "id": tid,
                "vector": vec.tolist(), # Contextual Vector
                "index": i
            })
        
        return result

    @property
    def dimension(self) -> int:
        return self._dim if self._dim else settings.VECTOR_DIM

    @property
    def name(self) -> str:
        return self.model_name

# --- The Context Manager (Factory) ---
class Embedder:
    def __init__(self, strategy_type: str = "local", **kwargs):
        self.strategy_type = strategy_type
        self.kwargs = kwargs
        
        # Factory Logic
        if strategy_type == "local":
            self.strategy = LocalHFStrategy(
                model_name=kwargs.get("model_name", settings.MODEL_NAME),
                device=kwargs.get("device", settings.DEVICE)
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy_type}")

    def __enter__(self):
        """Resource Allocation"""
        self.strategy.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Resource Cleanup"""
        # We keep the model loaded for the server, but this enables 'with' usage for scripts.
        pass 

    def load(self):
        self.strategy.load()

    def unload(self):
        self.strategy.unload()

    def encode(self, text) -> np.ndarray:
        return self.strategy.encode(text)

    def tokenize(self, text) -> List[Dict]:
        return self.strategy.tokenize(text)

    @property
    def dimension(self) -> int:
        return self.strategy.dimension
    
    @property
    def model_name(self) -> str:
        return self.strategy.name
