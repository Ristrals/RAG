# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from abc import ABC, abstractmethod
from pathlib import Path

from src.lib import Chunk


class Chunker(ABC):
    """ Chunker class """
    def __init__(self, max_chunk_size: int) -> None:
        self.max_chunk_size: int = max_chunk_size
        self._project_dir: str = ""
        self._files_list: list[Path] = []
        self._current_file_path: Path = Path()
        self._file_content: str = ""
        self._index_cursor: int = 0
        self.chunks: list[Chunk] = []

    def chunk_files(self, files_dict) -> None:
        """Chunks files into chunks"""

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

    @abstractmethod
    def _chunk_file(self) -> None:
        """Slices files into sections based on recovered indexations"""
        pass

    @abstractmethod
    def _create_chunks(self, content: str, start_index: int, hierarchy: str) -> None:
        """Chunking respective to max size chunking parameter"""
        pass

    @abstractmethod
    def _chunk_large_paragraphs(self, paragraph: str, hierarchy: str | None) -> list[Chunk]:
        """Splits an oversized code block into sub-chunks"""

        hierarchy_context_prefix: str = f"{hierarchy}" if hierarchy else ""
        paragraph_part: int = 1
        chunk_list: list[Chunk] = []

        while paragraph:
            part_context_prefix: str = hierarchy_context_prefix + f" (Part {paragraph_part})" if hierarchy else f"Part {paragraph_part}"  # noqa: E501
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
