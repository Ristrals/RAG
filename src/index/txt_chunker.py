# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from src.index import Chunker


class TxtChunker(Chunker):
    """Chunker specialized for plain text files."""

    def __init__(self, max_chunk_size: int) -> None:
        """Initialize a text chunker.

        Args:
            max_chunk_size: Maximum number of characters allowed per chunk.

        """
        super().__init__(max_chunk_size)

    def _chunk_file(self) -> None:
        """Slice plain text content without structural parsing.

        """
        self._chunk_process(
            content=self._file_content,
            start_index=0,
            hierarchy=""
        )

    def _chunk_process(self, content: str, start_index: int, hierarchy: str) -> None:
        """Normalize plain text and produce chunks.

        Args:
            content: Text content to process.
            start_index: Section start offset in the source file.
            hierarchy: Optional hierarchy label associated with the section.

        """

        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""
        raw_body: str = content
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self._index_cursor = start_index + leading_whitespace_offset
        if not body:
            return

        self._create_chunks(context_prefix, hierarchy, body)
