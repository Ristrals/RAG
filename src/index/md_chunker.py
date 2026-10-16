# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.index import Chunker
from src.lib import HeaderNode


class MDChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)
        self._headers: list[HeaderNode] = []
        self._in_code_block: bool = False

    def _chunk_file(self) -> None:
        """Slices files into sections based on recovered headers"""

        self._get_headers()

        if not self._headers:
            self._chunk_process(
                content=self._file_content,
                start_index=0,
                hierarchy=""
            )
            return

        if self._headers[0].start_index > 0:
            preamble_content = self._file_content[:self._headers[0].start_index]
            self._chunk_process(
                content=preamble_content,
                start_index=0,
                hierarchy=""
            )

        for idx, header in enumerate(self._headers):
            start_index = header.start_index
            end_index = self._headers[idx + 1].start_index if idx + 1 < len(self._headers) else len(self._file_content)
            content = self._file_content[start_index:end_index]
            self._chunk_process(
                content=content,
                start_index=start_index,
                hierarchy=header.hierarchy
            )

    def _get_headers(self) -> None:
        """Recovers all MD file headers"""

        self._headers = []
        self._in_code_block = False
        stack: list[tuple[int, str]] = []
        current_offset = 0

        for line in self._file_content.splitlines(keepends=True):
            if line.strip().startswith("```"):
                self._in_code_block = not self._in_code_block
            elif not self._in_code_block:
                header = self._is_header(line)
                if header:
                    level, title = header
                    while stack and stack[-1][0] >= level:
                        stack.pop()
                    stack.append(header)
                    self._headers.append(HeaderNode(
                            level=level,
                            title=title,
                            start_index=current_offset,
                            hierarchy=" > ".join(t for _, t in stack)
                    ))

            current_offset += len(line)

    def _chunk_process(self, content: str, start_index: int, hierarchy: str) -> None:
        """Recovers essential elements and proceeds to chunk"""

        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""
        lines: list[str] = content.splitlines(keepends=True)
        header_offset: int = len(lines[0]) if lines and self._is_header(lines[0]) else 0
        body_lines: list[str] = lines[1:] if header_offset > 0 else lines
        raw_body: str = "".join(body_lines)
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self._index_cursor = start_index + header_offset + leading_whitespace_offset
        if not body:
            return

        self._create_chunks(context_prefix, hierarchy, body)

    def _is_header(self, line: str) -> tuple[int, str] | None:
        """Checks if a line is a header and returns its level and title if true"""

        stripped_line = line.strip()
        if not stripped_line.startswith("#"):
            return None

        level = len(stripped_line) - len(stripped_line.lstrip("#"))
        if not (1 <= level <= 6):
            return None

        remainder = stripped_line[level:]
        if remainder and not remainder[0].isspace():
            return None

        title = remainder.strip()

        return level, title


if __name__ == "__main__":
    mdchunker = MDChunker(2000)
    md_file = {
        "RAGAgainstTheMachine": [Path("README.md")]
    }
    mdchunker.chunk_files(md_file)

    for i, chunk in enumerate(mdchunker.chunks):
        print(f"--- CHUNK {i + 1} ---")
        print(f"Project:   {chunk.project}")
        print(f"File path:   {chunk.file_path}")
        print(f"Hierarchy:   {chunk.hierarchy}")
        print(f"Start Index: {chunk.start_index}")
        print(f"End Index:   {chunk.end_index}")
        print(f"Content Length: {len(chunk.content)}")
        print("Content:\n")
        print(chunk.content)
        print("\n" + "=" * 40 + "\n")
