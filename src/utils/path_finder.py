# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

class PathFinder:
    _DEFAULT_RAW_DIR = Path("data/raw")
    _DEFAULT_PROCESSED_DIR = Path("data/processed")
    _DEFAULT_STATE_DIR = Path("data/state")

    def __init__(
        self, dataset_path: Path | None = None,
        save_directory: Path | None = None,
        student_search_results_path: Path | None = None
    ) -> None:
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
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.bm25_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def secure_save_directory(self) -> None:
        assert isinstance(self.save_dir, Path)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_file_reading(path: Path) -> None:
        """Raises a FileNotFoundError if an expected input path does not exist."""
        try:
            if not path.exists():
                raise FileNotFoundError()
        except FileNotFoundError as fnfe:
            raise Exception(fnfe)  # TO BE HANDLED CUSTOM ERROR

    @property
    def state_path(self) -> Path:
        return self.state_dir / "rag_state.json"

    @property
    def rag_state_bm25_path(self) -> Path:
        return self.state_dir / "rag_state_bm25.json"

    @property
    def rag_state_vector_path(self) -> Path:
        return self.state_dir / "rag_state_vector.json"

    @property
    def docsrc_path(self) -> Path:
        return self.processed_dir / "std_index.json"

    @property
    def database_path(self) -> Path:
        return self.bm25_dir / "bm25.db"

    @property
    def link_path(self) -> Path:
        return self.bm25_dir / "std_bm25_link.json"