from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env explicitly into os.environ so libraries like skipping huggingface_hub pick them up
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "LSV Engine"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    FIREWALL_THRESHOLD: float = 0.45
    LOAD_DEMOS: bool = False
    INGEST_BATCH_SIZE: int = 32
    INGEST_CHUNK_OVERLAP_PCT: float = 0.15
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    # Assuming backend/ is the root for execution or relative to it
    # Adjust based on where main.py is run. 
    # If running from backend/: BASE_DIR is backend/
    
    DATA_DIR: Path = BASE_DIR / "data"
    LANCEDB_URI: Path = DATA_DIR / "lancedb"
    CONTEXT_DB_PATH: Path = DATA_DIR / "context.db"
    VOCAB_PATH: Path = BASE_DIR.parent / "public" / "vocab.txt" 
    
    # Model Config
    MODEL_NAME: str = "BAAI/bge-m3"
    DEVICE: str = "cpu" # 'cuda' if available
    HF_TOKEN: Optional[str] = None
    HF_HUB_ETAG_TIMEOUT: int = 30
    HF_HUB_DOWNLOAD_TIMEOUT: int = 300
    
    # Vector Config
    VECTOR_DIM: int = 1024
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure data directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.LANCEDB_URI.mkdir(parents=True, exist_ok=True)
