# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pydantic import BaseModel
from pathlib import Path
from hashlib import sha256

from src.lib import MinSrc, Chunk

# MAXIMAL SOURCE
class DocumentSource(BaseModel):
    """Complete metadata source models used under the hood"""

    id: str
    text: str
    content_hash: str
    project: str
    file_path: str
    hierarchy: str
    first_character_index: int
    last_character_index: int

    @classmethod
    def from_chunk(cls, chunk: Chunk):
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
        return MinSrc(
            file_path=self.file_path,
            first_character_index=self.first_character_index,
            last_character_index=self.last_character_index,
        )


# GROUND TRUTH
class GroundTruthQuestion(BaseModel):
    question_id: str
    question: str
    answer: str
    sources: list[MinSrc]
    difficulty: str
    is_valid: bool


class GroundTruthDataset(BaseModel):
    rag_questions: list[GroundTruthQuestion]


#  RAG STATE:
class FileState(BaseModel):
    file_path: Path
    content_hash: str


class ProjectState(BaseModel):
    project: Path
    files: list[FileState]


class RAGState(BaseModel):
    rag_states: list[ProjectState]

    def get_project_state(self, project_name: Path | str) -> ProjectState | None:
        target = str(project_name)
        return next((p for p in self.rag_states if str(p.project) == target or Path(p.project).name == target), None)

    def get_file_state(self, project_name: Path | str, target_path: Path | str) -> FileState | None:
        """Finds and returns a specific FileState by project name and file path."""

        project = self.get_project_state(project_name)
        if not project:
            return None
        target_str = str(target_path)
        return next((f for f in project.files if str(f.file_path) == target_str), None)

    def add_file_state(self, project_name: Path, file_state: FileState) -> None:
        """Adds a FileState to a project, updating it if it already exists or creating the project if missing."""

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

    def remove_file_states(self, files_to_remove: list[Path | str]) -> None:
        """Removes specified file paths from all project states."""

        target_strs = {str(f) for f in files_to_remove}
        for proj in self.rag_states:
            proj.files = [f for f in proj.files if str(f.file_path) not in target_strs]


# API PAYLOADS
# Indexing
class APIIndex(BaseModel):
    max_chunk_size: int


# Evaluation
class APIEvaluate(BaseModel):
    student_result_path: str
    ground_truth_path: str


# Singular search & answer
class APIQuery(BaseModel):
    question: str
    k: int


# Search dataset
class APIDatasetSearch(BaseModel):
    dataset_path: str
    k: int
    save_directory_path: str


# Answer dataset
class APIDatasetAnswer(BaseModel):
    student_result_path: str
    save_directory_path: str