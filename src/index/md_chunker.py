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
        """Slices files into sections and merges adjacent sections up to max_chunk_size."""

        self._get_headers()
        sections = []

        # 1. Collect Preamble if it exists
        if self._headers and self._headers[0].start_index > 0:
            preamble_content = self._file_content[:self._headers[0].start_index]
            if preamble_content.strip():
                sections.append((0, "", preamble_content))

        # 2. Collect all header sections
        for idx, header in enumerate(self._headers):
            start_index = header.start_index
            end_index = self._headers[idx + 1].start_index if idx + 1 < len(self._headers) else len(self._file_content)
            content = self._file_content[start_index:end_index]
            sections.append((start_index, header.hierarchy, content))

        if not sections:
            return

        # 3. Rolling Merge Buffer Logic
        buffer_hierarchy = ""
        buffer_content: list[str] = []
        buffer_start_index = sections[0][0]

        for start_index, hierarchy, content in sections:
            # Determine the context prefix for this candidate section
            prefix = f"# Context: {hierarchy}\n\n" if hierarchy else ""

            # Calculate total size if we append this section to the current buffer
            current_body = "".join(buffer_content)
            candidate_body = current_body + content
            candidate_total_len = len(prefix) + len(candidate_body)

            # If the buffer is not empty and adding this section exceeds max_chunk_size, flush first
            if buffer_content and candidate_total_len > self.max_chunk_size:
                self._flush_buffer(buffer_hierarchy, buffer_content, buffer_start_index)
                buffer_hierarchy = hierarchy
                buffer_content = [content]
                buffer_start_index = start_index
            else:
                if not buffer_content:
                    buffer_hierarchy = hierarchy
                    buffer_start_index = start_index
                buffer_content.append(content)

        # Flush any remaining content in the buffer
        if buffer_content:
            self._flush_buffer(buffer_hierarchy, buffer_content, buffer_start_index)

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

    def _flush_buffer(self, hierarchy: str, content_parts: list[str], start_index: int) -> None:
        """Helper to process and create chunks from accumulated buffer parts."""
        combined_content = "".join(content_parts)
        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""

        lines: list[str] = combined_content.splitlines(keepends=True)
        header_offset: int = len(lines[0]) if lines and self._is_header(lines[0]) else 0
        body_lines: list[str] = lines[1:] if header_offset > 0 else lines
        raw_body: str = "".join(body_lines)
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()

        self._index_cursor = start_index + header_offset + leading_whitespace_offset
        if not body:
            return

        self._create_chunks(context_prefix, hierarchy, body)


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
