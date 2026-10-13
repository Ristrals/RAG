# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pydantic import BaseModel
from hashlib import sha256

from src.lib import MinSrc, Chunk


class DocumentSource(BaseModel):
    """Complete meta-data source models used under the hood"""

    id: str
    text: str
    content_hash: str
    project: str
    file_path: str
    hierarchy: str
    first_character_index: int
    last_character_index: int

    @classmethod
    def from_chunk(cls, chunk: Chunk):
        raw_id = f"{chunk.project}:{chunk.file_path}:{chunk.start_index}-{chunk.end_index}"
        doc_id = f"{chunk.project}_{sha256(raw_id.encode('utf-8')).hexdigest()[:16]}"

        content_hash = sha256(chunk.content.encode("utf-8")).hexdigest()

        return cls(
            id=doc_id,
            text=chunk.content,
            content_hash=content_hash,
            project=chunk.project,
            file_path=str(chunk.file_path),
            hierarchy=chunk.hierarchy,
            first_character_index=chunk.start_index,
            last_character_index=chunk.end_index,
        )

    def to_minimal_source(self) -> MinSrc:
        return MinSrc(
            file_path=self.file_path,
            first_character_index=self.first_character_index,
            last_character_index=self.last_character_index,
        )
