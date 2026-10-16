# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import ast
from pathlib import Path

from src.index import Chunker
from src.lib import CodeNode


class PYChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)
        self._code_nodes: list[CodeNode] = []

    def _chunk_file(self) -> None:
        """Slices files into sections based on recovered sections"""

        self._get_nodes()

        if not self._code_nodes:
            self._chunk_process(
                content=self._file_content,
                start_index=0,
                hierarchy=""
            )
            return

        if self._code_nodes[0].start_index > 0:
            preamble_content = self._file_content[:self._code_nodes[0].start_index]
            self._chunk_process(
                content=preamble_content,
                start_index=0,
                hierarchy="Preamble"
            )

        for node in self._code_nodes:
            content = self._file_content[node.start_index:node.end_index]
            self._chunk_process(
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

    def _chunk_process(self, content: str, start_index: int, hierarchy: str) -> None:
        """Recovers essential elements and chunk"""

        context_prefix: str = f"# Context: {hierarchy}\n\n" if hierarchy else ""
        raw_body: str = content
        leading_whitespace_offset: int = len(raw_body) - len(raw_body.lstrip())
        body: str = raw_body.strip()
        self._index_cursor = start_index + leading_whitespace_offset
        if not body:
            return

        self._create_chunks(context_prefix, hierarchy, body)

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
