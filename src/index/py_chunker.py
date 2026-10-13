# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import ast
from pathlib import Path
from collections import deque

from src.index import Chunker
from src.lib import CodeNode, Chunk


class PYChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)
        self._project_dir: str = ""
        self._files_list: list[Path] = []
        self._current_file_path: Path = Path()
        self._file_content: str = ""
        self._code_nodes: list[CodeNode] = []
        self._index_cursor: int = 0
        self.chunks: list[Chunk] = []

    def chunk_files(self, files_dict) -> None:
        """Chunk files into chunks"""

        self.chunks.clear()
        for project, files in files_dict.items():
            self._project_dir = project
            self._files_list = files
            self._process_project_files()

    def _process_project_files(self) -> None:
        """Processes project files"""

        for file in self._files_list:
            self._index_cursor = 0
            self._current_file_path = file
            with file.open(mode="r", encoding="utf-8") as content:
                self._file_content = content.read()
            self._chunk_file()

    def _chunk_file(self) -> None:
        """Slices files into sections based on recovered headers"""

        self._get_nodes()

        if not self._code_nodes:
            self._create_chunks(
                content=self._file_content,
                start_index=0,
                hierarchy=""
            )
            return

        if self._code_nodes[0].start_index > 0:
            preamble_content = self._file_content[:self._code_nodes[0].start_index]
            self._create_chunks(
                content=preamble_content,
                start_index=0,
                hierarchy="Preamble"
            )

        for node in self._code_nodes:
            content = self._file_content[node.start_index:node.end_index]
            self._create_chunks(
                content=content,
                start_index=node.start_index,
                hierarchy=node.hierarchy
            )

    def _get_nodes(self) -> None:
        """Recovers all MD file headers"""

        self._code_nodes = []

        if not self._file_content.strip():
            return

        try:
            ast_tree = ast.parse(str(self._file_content))
        except SyntaxError:
            # TO DO: Insert Error handling
            return

        line_offsets: list[int] = self._build_line_offsets()

        for node in ast_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.decorator_list[0].lineno if node.decorator_list else node.lineno
                start_idx: int = line_offsets[start_line - 1]
                end_idx: int = line_offsets[node.end_lineno - 1] + node.end_col_offset

                self._code_nodes.append(CodeNode(
                    name=node.name,
                    node_type="function",  # "class", "function", "method", "preamble"
                    start_index=start_idx,
                    end_index=end_idx,
                    hierarchy=node.name
                ))

            elif isinstance(node, ast.ClassDef):
                class_start_line = node.decorator_list[0].lineno if node.decorator_list else node.lineno
                class_start_idx: int = line_offsets[class_start_line - 1]

                methods = [
                    child for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]

                if methods:
                    first_method_start_line = (
                        methods[0].decorator_list[0].lineno
                        if methods[0].decorator_list
                        else methods[0].lineno
                    )
                    preamble_end_idx: int = line_offsets[first_method_start_line - 1]
                else:
                    preamble_end_idx: int = line_offsets[node.end_lineno - 1] + node.end_col_offset

                preamble_text = self._file_content[class_start_idx:preamble_end_idx].strip()
                preamble_lines = [
                    line.strip() for line in preamble_text.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]

                if len(preamble_lines) > 1 or not methods:
                    self._code_nodes.append(CodeNode(
                        name=f"{node.name} (Preamble)",
                        node_type="class_preamble",
                        start_index=class_start_idx,
                        end_index=preamble_end_idx,
                        hierarchy=node.name
                    ))

                for method in methods:
                    m_start_line = method.decorator_list[0].lineno if method.decorator_list else method.lineno
                    m_start = line_offsets[m_start_line - 1]
                    m_end = line_offsets[method.end_lineno - 1] + method.end_col_offset
                    self._code_nodes.append(CodeNode(
                        name=method.name,
                        node_type="method",
                        start_index=m_start,
                        end_index=m_end,
                        hierarchy=f"{node.name} > {method.name}"
                    ))

    def _create_chunks(self, content: str, start_index: int, hierarchy: str) -> None:
        """Chunking respective to max size chunking parameter."""
        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""

        raw_body: str = content
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self._index_cursor = start_index + leading_whitespace_offset

        if not body:
            return

        formated_chunk: str = context_prefix + body

        # 1. Block fits within max_chunk_size
        if len(formated_chunk) <= self.max_chunk_size:
            self.chunks.append(Chunk(
                content=formated_chunk,
                start_index=self._index_cursor,
                end_index=self._index_cursor + len(body),
                hierarchy=hierarchy,
                file_path=self._current_file_path,
                project=self._project_dir
            ))
            return

        # 2. Block exceeds max_chunk_size -> Split into sub-chunks
        paragraphs: deque[str] = deque(body.split("\n\n"))
        par_transition_offset: int = 2
        max_body_char: int = self.max_chunk_size - len(context_prefix)

        while paragraphs:
            chunk_paragraphs: list[str] = []
            current_chunk_len: int = 0
            chunk_start_offset: int = self._index_cursor

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
                    self._index_cursor += par_transition_offset
                    break

                paragraphs.popleft()
                chunk_paragraphs.append(next_par)
                current_chunk_len += separator_len + p_len

            if chunk_paragraphs:
                chunk_body = "\n\n".join(chunk_paragraphs)
                chunk_end_offset = chunk_start_offset + len(chunk_body)

                self.chunks.append(Chunk(
                    content=context_prefix + chunk_body,
                    start_index=chunk_start_offset,
                    end_index=chunk_end_offset,
                    hierarchy=hierarchy,
                    file_path=self._current_file_path,
                    project=self._project_dir
                ))

                self._index_cursor = chunk_end_offset + par_transition_offset

    def _chunk_large_paragraphs(self, paragraph: str, hierarchy: str | None) -> list[Chunk]:
        """Splits an oversized code block into sub-chunks"""

        hierarchy_context_prefix: str = f"{hierarchy}" if hierarchy else ""
        paragraph_part: int = 1
        chunk_list: list[Chunk] = []

        while paragraph:
            part_context_prefix: str = (
                hierarchy_context_prefix + f" (Part {paragraph_part})"
                if hierarchy else f"Part {paragraph_part}"
            )
            complete_context_prefix: str = f"# Context: {part_context_prefix}\n\n"
            max_paragraph_char: int = self.max_chunk_size - len(complete_context_prefix)
            paragraph_slice: str = paragraph[:max_paragraph_char]
            current_chunk: str = complete_context_prefix + paragraph_slice
            start_index: int = self._index_cursor
            end_index: int = self._index_cursor + len(paragraph_slice)

            chunk_list.append(Chunk(
                content=current_chunk,
                start_index=start_index,
                end_index=end_index,
                hierarchy=part_context_prefix.strip(),
                file_path=self._current_file_path,
                project=self._project_dir
            ))

            paragraph = paragraph[max_paragraph_char:]
            paragraph_part += 1
            self._index_cursor = end_index

        return chunk_list

    def _build_line_offsets(self) -> list[int]:
        offsets = [0]
        current = 0
        for line in self._file_content.splitlines(keepends=True):
            current += len(line)
            offsets.append(current)
        return offsets


if __name__ == "__main__":
    pychunker = PYChunker(2000)
    py_file = {
        "RAGAgainstTheMachine": [Path("src/index/md_chunker.py")]
    }
    pychunker.chunk_files(py_file)

    for i, chunk in enumerate(pychunker.chunks):
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
