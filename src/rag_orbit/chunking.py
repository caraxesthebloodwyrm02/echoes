from dataclasses import dataclass
from hashlib import sha256
from typing import List, Optional, Tuple


@dataclass
class ChunkMetadata:
    chunk_id: str
    source_document: str
    category: Optional[str]
    checksum: str

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "source_document": self.source_document,
            "category": self.category,
            "checksum": self.checksum,
        }


@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata

    def compute_checksum(self) -> str:
        return sha256(self.text.encode("utf-8")).hexdigest()


class DocumentChunker:
    def __init__(self, chunk_size: int = 200, overlap: int = 20):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, text: str, source_document: str, category: Optional[str] = None) -> List[Chunk]:
        if not text:
            return []
        words = text.split()
        chunks: List[Chunk] = []
        step = max(1, self.chunk_size - self.overlap)
        idx = 0
        n = len(words)
        while idx < n:
            segment = words[idx: idx + self.chunk_size]
            if not segment:
                break
            chunk_text = " ".join(segment)
            chunk_id = f"{source_document}:{len(chunks)}"
            checksum = sha256(chunk_text.encode("utf-8")).hexdigest()
            chunks.append(
                Chunk(
                    text=chunk_text,
                    metadata=ChunkMetadata(
                        chunk_id=chunk_id,
                        source_document=source_document,
                        category=category,
                        checksum=checksum,
                    ),
                )
            )
            idx += step
        return chunks

    def chunk_batch(self, documents: List[Tuple[str, str, Optional[str]]]) -> List[Chunk]:
        out: List[Chunk] = []
        for text, source_document, category in documents:
            out.extend(self.chunk_document(text, source_document, category))
        return out

    def validate_chunks(self, chunks: List[Chunk]):
        errors = []
        for chunk in chunks:
            if not chunk.text.strip():
                errors.append("empty_chunk")
            if chunk.compute_checksum() != chunk.metadata.checksum:
                errors.append(f"checksum_mismatch:{chunk.metadata.chunk_id}")
        return len(errors) == 0, errors


def create_standard_chunker() -> DocumentChunker:
    return DocumentChunker(chunk_size=120, overlap=20)
