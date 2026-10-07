# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path
from collections import deque
from dataclasses import dataclass

from src.index.chunker import Chunker


@dataclass
class HeaderNode:
    level: int
    title: str
    start_index: int
    hierarchy : str

@dataclass
class Chunk:
    content: str
    start_index: int
    end_index: int
    hierarchy: str

class MDChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)
        self.project_dir: str = ""
        self.files_list: list[Path] = []
        self.file_content: str = ""
        self.headers: list[HeaderNode] = []
        self.chunks: list[Chunk] = []
        self.index_cursor: int = 0
        self.in_code_block: bool = False

    def chunk_files(self, files_dict) -> None:
        """Chunks files into chunks"""

        self.chunks.clear()
        for project, files in files_dict.items():
            self.project_dir = project
            self.files_list = files
            self._process_project_files()

    def _process_project_files(self) -> None:
        """Processes project files"""

        for file in self.files_list:
            self.index_cursor = 0
            with file.open(mode="r", encoding="utf-8") as content:
                self.file_content = content.read()
            self._chunk_file()

    def _chunk_file(self) -> None:
        """Slices files into sections based on recovered headers"""

        self._get_headers()

        if not self.headers:
            self._create_chunks(
                    content = self.file_content,
                    start_index = 0,
                    hierarchy = ""
            )
            return

        if self.headers[0].start_index > 0:
            preamble_content = self.file_content[:self.headers[0].start_index]
            self._create_chunks(
                    content = preamble_content,
                    start_index = 0,
                    hierarchy = ""
            )

        for i, header in enumerate(self.headers):
            start_index = header.start_index
            end_index = self.headers[i + 1].start_index if i + 1 < len(self.headers) else len(self.file_content)
            content = self.file_content[start_index:end_index]
            self._create_chunks(
                content = content,
                start_index = start_index,
                hierarchy = header.hierarchy
            )

    def _get_headers(self) -> None:
        """Recovers all MD file headers"""

        self.headers = []
        self.in_code_block = False
        stack: list[tuple[int, str]] = []
        current_offset = 0

        for line in self.file_content.splitlines(keepends=True):
            if line.strip().startswith("```"):
                self.in_code_block = not self.in_code_block
            elif not self.in_code_block:
                header = self._is_header(line)
                if header:
                    level, title = header
                    while stack and stack[-1][0] >= level:
                        stack.pop()
                    stack.append(header)
                    self.headers.append(HeaderNode(
                            level = level,
                            title = title,
                            start_index = current_offset,
                            hierarchy = " > ".join(t for _, t in stack)
                    ))

            current_offset += len(line)

    def _create_chunks(self, content: str, start_index: int, hierarchy: str) -> None:
        """Chunking respective to max size chunking parameter"""

        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""

        lines: list[str] = content.splitlines(keepends=True)
        header_offset: int = len(lines[0]) if lines and self._is_header(lines[0]) else 0
        body_lines: list[str] = lines[1:] if header_offset > 0 else lines
        raw_body: str = "".join(body_lines)
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self.index_cursor = start_index + header_offset + leading_whitespace_offset

        if not body:
            return

        formated_chunk: str = context_prefix + body
        if len(formated_chunk) <= self.max_chunk_size:
            self.chunks.append(Chunk(
                content = formated_chunk,
                start_index = self.index_cursor,
                end_index = self.index_cursor + len(body),
                hierarchy = hierarchy
            ))
            return

        paragraphs: deque[str] = deque(body.split("\n\n"))
        par_transition_offset: int = 2
        max_body_char: int = self.max_chunk_size - len(context_prefix)

        while paragraphs:
            chunk_paragraphs: list[str] = []
            current_chunk_len: int = 0
            chunk_start_offset: int = self.index_cursor

            while paragraphs:
                next_par = paragraphs[0]
                p_len = len(next_par)
                separator_len = par_transition_offset if chunk_paragraphs else 0

                if chunk_paragraphs and (current_chunk_len + separator_len + p_len > max_body_char):
                    break

                if not chunk_paragraphs and p_len > max_body_char:
                    large_par = paragraphs.popleft()
                    large_chunks = self._chunk_large_paragraphs(
                        paragraph=large_par,
                        hierarchy=hierarchy
                    )
                    self.chunks.extend(large_chunks)
                    self.index_cursor += par_transition_offset
                    break

                paragraphs.popleft()
                chunk_paragraphs.append(next_par)
                current_chunk_len += separator_len + p_len

            if chunk_paragraphs:
                chunk_body = "\n\n".join(chunk_paragraphs)
                chunk_end_offset = chunk_start_offset + len(chunk_body)

                self.chunks.append(Chunk(
                    content = context_prefix + chunk_body,
                    start_index = chunk_start_offset,
                    end_index = chunk_end_offset,
                    hierarchy = hierarchy
                ))

                self.index_cursor = chunk_end_offset + par_transition_offset

    def _chunk_large_paragraphs(
            self, paragraph: str,
            hierarchy: str | None) -> list[Chunk]:

        hierarchy_context_prefix: str = f"{hierarchy}" if hierarchy else ""
        paragraph_part: int = 1
        chunk_list: list[Chunk] = []

        while paragraph:
            part_context_prefix: str = hierarchy_context_prefix + f" (Part {paragraph_part})" if hierarchy else f"Part {paragraph_part}"  # noqa: E501
            complete_context_prefix: str = f"# Context: {part_context_prefix}\n\n"
            max_paragraph_char: int = self.max_chunk_size - len(complete_context_prefix)
            paragraph_slice: str = paragraph[:max_paragraph_char]
            chunk: str = complete_context_prefix + paragraph_slice
            start_index: int = self.index_cursor
            end_index: int = self.index_cursor + len(paragraph_slice)

            chunk_list.append(Chunk(
                content = chunk,
                start_index = start_index,
                end_index = end_index,
                hierarchy = part_context_prefix.strip()
            ))

            paragraph = paragraph[max_paragraph_char:]
            paragraph_part += 1
            self.index_cursor = end_index

        return chunk_list

    def _is_header(self, line: str) -> tuple[int, str] | None:
        """Checks if a line is a header and returns its level and title if true"""

        stripped_line = line.strip()
        if not stripped_line.startswith("#") :
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
        print(f"Hierarchy:   {chunk.hierarchy}")
        print(f"Start Index: {chunk.start_index}")
        print(f"End Index:   {chunk.end_index}")
        print(f"Content Length: {len(chunk.content)}")
        print("Content:")
        print(chunk.content)
        print("\n" + "=" * 40 + "\n")