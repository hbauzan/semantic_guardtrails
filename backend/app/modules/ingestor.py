import re
from pathlib import Path
from typing import List, Generator
from pydantic import BaseModel
from app.core.config import settings

class Chunk(BaseModel):
    text: str
    metadata: dict

class Ingestor:
    def __init__(self, chunk_size: int = 2048, chunk_overlap: int = 256):
        self.chunk_size = chunk_size
        # Dynamically calculated if specific overlap not provided
        self.chunk_overlap = int(chunk_size * settings.INGEST_CHUNK_OVERLAP_PCT) if chunk_overlap == 50 else chunk_overlap

    def load_file(self, file_path: Path) -> Generator[Chunk, None, None]:
        """Loads a file and returns a generator of text chunks."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == '.txt':
            yield from self._load_text(file_path)
        elif file_path.suffix.lower() == '.pdf':
            yield from self._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _load_text(self, file_path: Path) -> Generator[Chunk, None, None]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            # If it's a vocab file (one word per line), treat differently?
            # For now, let's assume standard text for chunking, 
            # or check if it looks like a vocab list.
            # User mentioned "vocab.txt", which is usually line-separated.
            # Let's support both: if many newlines, maybe treat lines as chunks?
            # For this generic ingestor, let's stick to sliding window for prose,
            # and line-based for lists.
            
            # Simple heuristic: if avg line length < 20 chars, maybe it's a list.
            lines = text.splitlines()
            if len(lines) > 0 and (len(text) / len(lines)) < 30:
                 for i, line in enumerate(lines):
                     if line.strip():
                         yield Chunk(text=line.strip(), metadata={"source": str(file_path), "line": i+1})
                 return

            yield from self._chunk_text(text, source=str(file_path))

    def _load_pdf(self, file_path: Path) -> Generator[Chunk, None, None]:
        try:
            import fitz # PyMuPDF
        except ImportError:
            raise ImportError("fitz (pymupdf) is required for PDF ingestion. pip install pymupdf")
        
        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            if text:
                yield from self._chunk_text(text, source=str(file_path), page=i+1)
        doc.close()

    def _chunk_text(self, text: str, **metadata) -> Generator[Chunk, None, None]:
        """Simple sliding window chunker."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at a space
            if end < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space != -1:
                    end = start + last_space
                    chunk_text = text[start:end]
            
            yield Chunk(text=chunk_text, metadata=metadata)
            
            step = len(chunk_text) - self.chunk_overlap
            if step <= 0:
                break
            start += step
