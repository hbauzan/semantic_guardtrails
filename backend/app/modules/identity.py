import pandas as pd
from typing import Optional, Dict
from app.modules.storage import Storage

class IdentityResolver:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.galaxy_map: Dict[str, int] = {}
        self._load_galaxy()

    def _load_galaxy(self):
        print("🌌 IdentityResolver: Loading Galaxy Vocabulary...")
        if self.storage.total_items == 0:
            print("⚠️ IdentityResolver: Vector Store is empty. Bypassing map loading.")
            return

        df = self.storage.get_all_vectors()
        
        if not df.empty and 'text' in df.columns and 'id' in df.columns:
            # Create a dictionary for O(1) lookup
            self.galaxy_map = dict(zip(df['text'], df['id']))
            print(f"🌌 IdentityResolver: Loaded {len(self.galaxy_map)} identities.")
        else:
            print("⚠️ IdentityResolver: 'text' or 'id' column missing in Galaxy Storage.")

    def get_galaxy_id(self, text: str) -> Optional[int]:
        return self.galaxy_map.get(text)
