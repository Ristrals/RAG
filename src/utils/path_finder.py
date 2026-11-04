# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

"""Path management utilities for indexing, retrieval, and state persistence."""

from pathlib import Path

from src.lib import ErrType
from src.utils import PathFinderError


class PathFinder:
    """Resolve and validate project paths used by the application.

    Attributes:
        raw_dir: Directory containing raw source projects to index.
        processed_dir: Directory containing processed index artifacts.
        state_dir: Directory containing synchronization state files.
        bm25_dir: Lexical index directory.
        vector_dir: Semantic index directory.
        dataset_path: Optional dataset input path.
        student_search_results_path: Optional student-results input path.
        save_dir: Optional output directory for generated files.
    """

    _DEFAULT_RAW_DIR = Path("data/raw")
    _DEFAULT_PROCESSED_DIR = Path("data/processed")
    _DEFAULT_STATE_DIR = Path("data/state")

    def __init__(
        self, dataset_path: Path | None = None,
        save_directory: Path | None = None,
        student_search_results_path: Path | None = None
    ) -> None:
        """Initialize path configuration and validate provided inputs.

        Args:
            dataset_path: Optional dataset file to load.
            save_directory: Optional directory where outputs are written.
            student_search_results_path: Optional student-results file to load.

        """
        self.raw_dir: Path = self._DEFAULT_RAW_DIR  # Raw project to chunk
        self.processed_dir: Path = self._DEFAULT_PROCESSED_DIR  # Indexed projects
        self.state_dir: Path = self._DEFAULT_STATE_DIR  # State sync
        self.bm25_dir: Path = self.processed_dir / "lexical"  # Dedicated to SQLite BM25
        self.vector_dir: Path = self.processed_dir / "semantic"  # Dedicated to ChromaDB

        self.dataset_path: Path | None = dataset_path  # Dataset folders
        if self.dataset_path:
            self.validate_file_reading(self.dataset_path)

        self.student_search_results_path: Path | None = student_search_results_path  # Answer results
        if self.student_search_results_path:
            self.validate_file_reading(self.student_search_results_path)

        self.save_dir: Path | None = save_directory  # Research results
        if self.save_dir:
            self.secure_save_directory()

    def secure_index_directories(self) -> None:
        """Create required indexing and state directories when missing.

        """
        try:
            self.raw_dir.mkdir(parents=True, exist_ok=True)
            self.bm25_dir.mkdir(parents=True, exist_ok=True)
            self.vector_dir.mkdir(parents=True, exist_ok=True)
            self.state_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise PathFinderError(ErrType.CRIT, e)

    def secure_save_directory(self) -> None:
        """Create the configured save directory when missing.

        """
        assert isinstance(self.save_dir, Path)
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise PathFinderError(ErrType.CRIT, e)

    @staticmethod
    def validate_file_reading(path: Path) -> None:
        """Validate that an input path exists before reading.

        Args:
            path: File path expected to exist.

        """

        if not path.exists():
            raise PathFinderError(
                    ErrType.CRIT,
                    FileNotFoundError(f"File '{path}' does not exist"))

    @property
    def state_path(self) -> Path:
        """Path to the generic RAG state file."""
        return self.state_dir / "rag_state.json"

    @property
    def rag_state_bm25_path(self) -> Path:
        """Path to the lexical backend RAG state file."""
        return self.state_dir / "rag_state_bm25.json"

    @property
    def rag_state_vector_path(self) -> Path:
        """Path to the semantic backend RAG state file."""
        return self.state_dir / "rag_state_vector.json"

    @property
    def docsrc_path(self) -> Path:
        """Path to persisted document-source metadata."""
        return self.processed_dir / "std_index.json"

    @property
    def database_path(self) -> Path:
        """Path to the SQLite BM25 database file."""
        return self.bm25_dir / "bm25.db"
