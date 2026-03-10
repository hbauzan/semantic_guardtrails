from app.modules.embedder import Embedder
from app.modules.storage import Storage
from app.modules.geometry import Geometry
from app.modules.context_vault import ContextVault
import pandas as pd

class GlobalState:
    embedder: Embedder = None
    storage: Storage = None
    geometry: Geometry = None
    context_vault: ContextVault = None
    # Cache for the Galaxy View / Probe
    galaxy_cache: pd.DataFrame = None 
    identity_resolver: "IdentityResolver" = None 
    firewall_threshold: float = 0.45 

state = GlobalState()

def get_embedder() -> Embedder:
    if not state.embedder:
        # Initialize Embedder (loads model)
        state.embedder = Embedder()
        state.embedder.load()
    return state.embedder

def get_storage() -> Storage:
    if not state.storage:
        # Ensure embedder is ready to get name/dim
        embedder = get_embedder()
        state.storage = Storage(
            model_name=embedder.model_name,
            dimension=embedder.dimension
        )
    return state.storage

def get_context_vault() -> ContextVault:
    if not state.context_vault:
        state.context_vault = ContextVault()
    return state.context_vault

def get_galaxy_cache(force_reload: bool = False) -> pd.DataFrame:
    """Lazy loads the full dataset for analysis."""
    if state.galaxy_cache is None or force_reload:
        print("🧠 Loading Galaxy Cache into Memory...")
        storage = get_storage()
        state.galaxy_cache = storage.get_all_vectors()
    return state.galaxy_cache

# Geometry is usually accessed via state directly or initialized on startup
if not state.geometry:
    state.geometry = Geometry()

from app.modules.identity import IdentityResolver

def get_identity_resolver() -> IdentityResolver:
    if not state.identity_resolver:
        print("🆔 Initializing Identity Resolver...")
        storage = get_storage()
        state.identity_resolver = IdentityResolver(storage)
    return state.identity_resolver
