# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.index import Chunker


class TxtChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)

    def _chunk_file(self) -> None:
        """Slices plain text or code files without header or AST parsing"""
        self._chunk_process(
            content=self._file_content,
            start_index=0,
            hierarchy=""
        )

    def _chunk_process(self, content: str, start_index: int, hierarchy: str) -> None:
        """Recovers essential elements and proceeds to chunk"""

        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""
        raw_body: str = content
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self._index_cursor = start_index + leading_whitespace_offset
        if not body:
            return

        self._create_chunks(context_prefix, hierarchy, body)


if __name__ == "__main__":
    txt_chunker = TxtChunker(2000)
    txt_file = {
        "RAGAgainstTheMachine": [Path("data/raw/vllm-0.10.1/CMakeLists.txt")]
    }
    txt_chunker.chunk_files(txt_file)

    for i, chunk in enumerate(txt_chunker.chunks):
        print(f"--- CHUNK {i + 1} ---")
        print(f"Project:     {chunk.project}")
        print(f"File path:   {chunk.file_path}")
        print(f"Hierarchy:   {chunk.hierarchy}")
        print(f"Start Index: {chunk.start_index}")
        print(f"End Index:   {chunk.end_index}")
        print(f"Content Length: {len(chunk.content)}")
        print("Content:\n")
        print(chunk.content)
        print("\n" + "=" * 40 + "\n")