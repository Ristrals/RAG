# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pydantic import BaseModel
from pathlib import Path
from hashlib import sha256

from src.lib import MinSrc, Chunk


# MAXIMAL SOURCE
class DocumentSource(BaseModel):
    """Complete indexed document metadata used internally.

    Attributes:
        id: Stable document identifier.
        text: Stored chunk text.
        content_hash: Hash of the chunk text content.
        project: Project name where the chunk originates.
        file_path: Original source file path.
        hierarchy: Section hierarchy metadata.
        first_character_index: Start offset in source file.
        last_character_index: End offset in source file.
    """

    id: str
    text: str
    content_hash: str
    project: str
    file_path: str
    hierarchy: str
    first_character_index: int
    last_character_index: int

    @classmethod
    def from_chunk(cls, chunk: Chunk) -> "DocumentSource":
        """Create a document source from a chunk instance.

        Args:
            chunk: Chunk object containing source metadata and text.

        Returns:
            Document source instance with generated identifier and hashes.
        """
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
        """Convert to the minimal source representation.

        Returns:
            Minimal source with file path and index boundaries.
        """
        return MinSrc(
            file_path=self.file_path,
            first_character_index=self.first_character_index,
            last_character_index=self.last_character_index,
        )


# GROUND TRUTH
class GroundTruthQuestion(BaseModel):
    """Ground-truth question/answer pair with validation metadata."""

    question_id: str
    question: str
    answer: str
    sources: list[MinSrc]
    difficulty: str
    is_valid: bool


class GroundTruthDataset(BaseModel):
    """Container for ground-truth RAG evaluation questions."""

    rag_questions: list[GroundTruthQuestion]


#  RAG STATE:
class FileState(BaseModel):
    """Tracked hash state for a single file in a project."""

    file_path: Path
    content_hash: str


class ProjectState(BaseModel):
    """Tracked state for all indexed files within one project."""

    project: Path
    files: list[FileState]


class RAGState(BaseModel):
    """Global state of indexed projects and their tracked files."""

    rag_states: list[ProjectState]

    def get_project_state(self, project_name: Path | str) -> ProjectState | None:
        """Return project state by path or project name.

        Args:
            project_name: Absolute path or project folder name.

        Returns:
            Matching project state or None when not found.
        """
        target = str(project_name)
        return next((p for p in self.rag_states if str(p.project) == target or Path(p.project).name == target), None)

    def get_file_state(self, project_name: Path | str, target_path: Path | str) -> FileState | None:
        """Return file state for a given project and file path.

        Args:
            project_name: Project path or folder name.
            target_path: File path to locate in project state.

        Returns:
            Matching file state or None when not found.
        """

        project = self.get_project_state(project_name)
        if not project:
            return None
        target_str = str(target_path)
        return next((f for f in project.files if str(f.file_path) == target_str), None)

    def add_file_state(self, project_name: Path, file_state: FileState) -> None:
        """Insert or update a file state in a project entry.

        Args:
            project_name: Project path owning the file.
            file_state: File state entry to add or update.

        """

        project = self.get_project_state(project_name)

        if project:
            existing_file = next((f for f in project.files if str(f.file_path) == str(file_state.file_path)), None)
            if existing_file:
                existing_file.content_hash = file_state.content_hash
            else:
                project.files.append(file_state)
        else:
            self.rag_states.append(
                ProjectState(project=project_name, files=[file_state])
            )

    def remove_file_states(self, files_to_remove: list[Path]) -> None:
        """Remove file states matching provided paths.

        Args:
            files_to_remove: File paths to remove from all project states.

        """

        target_strs = {str(f) for f in files_to_remove}
        for proj in self.rag_states:
            proj.files = [f for f in proj.files if str(f.file_path) not in target_strs]


# Interface PAYLOADS
# Indexing
class InterfaceIndex(BaseModel):
    """Payload for index commands.

    Attributes:
        max_chunk_size: Maximum number of characters per chunk.
    """

    max_chunk_size: int


# Evaluation
class InterfaceEvaluate(BaseModel):
    """Payload for evaluation commands."""

    student_search_results_path: str
    dataset_path: str


# Singular search & answer
class InterfaceQuery(BaseModel):
    """Payload for single query search or answer commands."""

    query: str
    k: int


# Search dataset
class InterfaceDatasetSearch(BaseModel):
    """Payload for dataset-wide search commands."""

    dataset_path: str
    k: int
    save_directory: str


# Answer dataset
class InterfaceDatasetAnswer(BaseModel):
    """Payload for dataset-wide answer commands."""

    student_search_result_path: str
    save_directory: str
