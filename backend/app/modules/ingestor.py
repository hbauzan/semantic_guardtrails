import re
from pathlib import Path
from typing import List, Generator
from pydantic import BaseModel

class Chunk(BaseModel):
    text: str
    metadata: dict

class Ingestor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_file(self, file_path: Path) -> List[Chunk]:
        """Loads a file and returns a list of text chunks."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == '.txt':
            return self._load_text(file_path)
        elif file_path.suffix.lower() == '.pdf':
            return self._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _load_text(self, file_path: Path) -> List[Chunk]:
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
                 return [Chunk(text=line.strip(), metadata={"source": str(file_path), "line": i+1}) 
                         for i, line in enumerate(lines) if line.strip()]

            return list(self._chunk_text(text, source=str(file_path)))

    def _load_pdf(self, file_path: Path) -> List[Chunk]:
        try:
            import pypdf
        except ImportError:
            raise ImportError("pypdf is required for PDF ingestion. pip install pypdf")
        
        reader = pypdf.PdfReader(file_path)
        chunks = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                curr_chunks = self._chunk_text(text, source=str(file_path), page=i+1)
                chunks.extend(curr_chunks)
        return chunks

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
            start += (len(chunk_text) - self.chunk_overlap)
