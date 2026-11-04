# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from abc import ABC, abstractmethod
from pathlib import Path
from collections import deque

from src.lib import Chunk


class Chunker(ABC):
    """Abstract base class for file chunking strategies.

    Attributes:
        max_chunk_size: Maximum number of characters allowed in a chunk.
        _project_dir: Current project identifier being processed.
        _files_list: Files queued for chunking in the current project.
        _current_file_path: Path of the file currently being chunked.
        _file_content: Raw content of the current file.
        _index_cursor: Cursor tracking offsets in the current file.
        chunks: Generated chunks accumulated during processing.
    """
    def __init__(self, max_chunk_size: int) -> None:
        self.max_chunk_size: int = max_chunk_size
        self._project_dir: str = ""
        self._files_list: list[Path] = []
        self._current_file_path: Path = Path()
        self._file_content: str = ""
        self._index_cursor: int = 0
        self.chunks: list[Chunk] = []

    def chunk_files(self, files_dict: dict[str, list[Path]]) -> None:
        """Chunk all files grouped by project.

        Args:
            files_dict: Mapping of project identifiers to the list of files
                that must be chunked.

        """

        self.chunks.clear()
        for project, files in files_dict.items():
            self._project_dir = project
            self._files_list = files
            self._process_project_files()

    def _process_project_files(self) -> None:
        """Read and chunk every file in the current project.

        """

        for file in self._files_list:
            self._index_cursor = 0
            self._current_file_path = file
            with file.open(mode="r", encoding="utf-8") as content:
                self._file_content = content.read()
            self._chunk_file()

    @abstractmethod
    def _chunk_file(self) -> None:
        """Slice the currently loaded file into semantic sections.

        """
        pass

    @abstractmethod
    def _chunk_process(self, content: str, start_index: int, hierarchy: str) -> None:
        """Apply chunking logic to a section of file content.

        Args:
            content: Section content to chunk.
            start_index: Starting offset of the section in the full file.
            hierarchy: Hierarchical label describing section context.

        """
        pass

    def _create_chunks(self, context_prefix: str, hierarchy: str, body: str) -> None:
        """Create one or more chunks from section content.

        Splits content according to ``max_chunk_size`` while preserving
        start/end offsets relative to the source file.

        Args:
            context_prefix: Prefix prepended to each chunk (metadata/context).
            hierarchy: Hierarchical label associated with the section.
            body: Raw section body to split into chunks.

        """

        formated_chunk: str = context_prefix + body
        if len(formated_chunk) <= self.max_chunk_size:
            self.chunks.append(Chunk(
                content=formated_chunk,
                start_index=self._index_cursor,
                end_index=self._index_cursor + len(body),
                hierarchy=hierarchy,
                file_path=self._current_file_path,
                project=self._project_dir
            ))
            # Advance cursor past this body section plus any trailing whitespace/newlines
            self._index_cursor += len(body)
            return

        paragraphs: deque[str] = deque(body.split("\n\n"))
        max_body_char: int = self.max_chunk_size - len(context_prefix)
        current_body_cursor: int = self._index_cursor

        while paragraphs:
            chunk_paragraphs: list[str] = []
            current_chunk_len: int = 0
            chunk_start_offset: int = current_body_cursor

            while paragraphs:
                next_par = paragraphs[0]
                p_len = len(next_par)
                separator_len = 2 if chunk_paragraphs else 0  # "\n\n" separator length

                if chunk_paragraphs and (current_chunk_len + separator_len + p_len > max_body_char):
                    break

                if not chunk_paragraphs and p_len > max_body_char:
                    large_par = paragraphs.popleft()
                    large_chunks = self._chunk_large_paragraphs(
                        paragraph=large_par,
                        hierarchy=hierarchy
                    )
                    self.chunks.extend(large_chunks)
                    current_body_cursor += len(large_par) + 2
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

                # Advance body cursor by the exact length of the chunk body plus paragraph spacing
                current_body_cursor = chunk_end_offset + 2

        self._index_cursor = current_body_cursor

    def _chunk_large_paragraphs(self, paragraph: str, hierarchy: str | None) -> list[Chunk]:
        """Split an oversized paragraph into multiple chunk parts.

        Args:
            paragraph: Oversized text block that cannot fit in one chunk.
            hierarchy: Optional hierarchy label to include in context.

        Returns:
            List of generated chunks representing paragraph parts.
        """

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
