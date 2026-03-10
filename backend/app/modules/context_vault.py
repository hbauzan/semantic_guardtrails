import sqlite3
from typing import List, Dict, Optional, Any
from app.core.config import settings
import threading

class ContextVault:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ContextVault, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.db_path = str(settings.CONTEXT_DB_PATH)
        self._init_db()
        self._initialized = True

    def _get_connection(self):
        """Returns a thread-local connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Initializes the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Dictionaries Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictionaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                description TEXT
            )
        """)

        # Definitions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                dictionary_id INTEGER NOT NULL,
                definition TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                FOREIGN KEY (dictionary_id) REFERENCES dictionaries (id) ON DELETE CASCADE
            )
        """)

        # Index for O(1) lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_definitions_token_id 
            ON definitions (token_id)
        """)

        conn.commit()
        conn.close()

    def create_dictionary(self, name: str, color: str = "#FFFFFF", description: str = "") -> int:
        """Creates a new dictionary and returns its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO dictionaries (name, color, description)
                VALUES (?, ?, ?)
            """, (name, color, description))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Already exists, get ID
            cursor.execute("SELECT id FROM dictionaries WHERE name = ?", (name,))
            return cursor.fetchone()['id']
        finally:
            conn.close()

    def add_definition(self, token_id: int, dictionary_name: str, definition: str, weight: float = 1.0):
        """Adds a definition to a token under a specific dictionary."""
        # Ensure dictionary exists
        dict_id = self.create_dictionary(dictionary_name)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO definitions (token_id, dictionary_id, definition, weight)
                VALUES (?, ?, ?, ?)
            """, (token_id, dict_id, definition, weight))
            conn.commit()
        finally:
            conn.close()

    def get_context(self, token_id: int) -> List[Dict[str, Any]]:
        """Retrieves all definitions for a specific token."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    d.name as dictionary,
                    d.color,
                    def.definition,
                    def.weight
                FROM definitions def
                JOIN dictionaries d ON def.dictionary_id = d.id
                WHERE def.token_id = ?
                ORDER BY d.name
            """, (token_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_defined_token_ids(self) -> set[int]:
        """Efficiently retrieves the set of all token IDs that have definitions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT token_id FROM definitions")
            rows = cursor.fetchall()
            return {row['token_id'] for row in rows}
        finally:
            conn.close()

    def wipe_definitions(self):
        """Wipes the definitions table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM definitions")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='definitions'")
            conn.commit()
            print("🧹 ContextVault: Definitions table wiped.")
        finally:
            conn.close()

    def delete_dictionary(self, name: str) -> bool:
        """Deletes a dictionary and its associated definitions (via CASCADE)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dictionaries WHERE name = ?", (name,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_dictionary_stats(self) -> List[Dict[str, Any]]:
        """Returns a summary of dictionaries and their term counts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT d.name, d.color, COUNT(def.id) as term_count
                FROM dictionaries d
                LEFT JOIN definitions def ON d.id = def.dictionary_id
                GROUP BY d.id, d.name, d.color
                ORDER BY term_count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
