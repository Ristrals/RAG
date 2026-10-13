# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

class PathFinder:
    _DEFAULT_RAW_DIR = Path("data/raw")
    _DEFAULT_PROCESSED_DIR = Path("data/processed")
    _DEFAULT_DATASETS_DIR = Path("data/datasets")
    _DEFAULT_OUTPUT_SEARCH_DIR = Path("data/output/search_results")
    _DEFAULT_OUTPUT_ANSWER_DIR = Path("data/output/search_results_and_answer")

    def __init__(
            self, save_directory: Path | None = None,
            data_set: Path | None = None,
            student_search_results: Path | None = None
    ) -> None:
        self.raw_dir: Path = self._DEFAULT_RAW_DIR  # Raw project to chunk
        self.processed_dir: Path = self._DEFAULT_PROCESSED_DIR  # Indexed projects
        self.bm25_dir: Path = self.processed_dir / "bm25_index"  # Dedicated to BM25
        self.vector_dir: Path = self.processed_dir / "vector"  # Dedicated to ChromaDB
        self.data_dir: Path = data_set if data_set else self._DEFAULT_DATASETS_DIR  # Dataset folders
        # Research results
        self.search_result_dir: Path = save_directory if save_directory else self._DEFAULT_OUTPUT_SEARCH_DIR
        # Answer results
        self.search_answer_dir: Path = student_search_results if student_search_results else self._DEFAULT_OUTPUT_ANSWER_DIR  # noqa: E501

    def secure_index_directories(self) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.bm25_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)

    def secure_search_answer_directories(self) -> None:
        self.search_result_dir.mkdir(parents=True, exist_ok=True)
        self.search_answer_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def secure_file_writing(file_or_dir_path: Path) -> None:
        """Helper to ensure the target output folder exists before writing a file."""
        if file_or_dir_path.suffix:  # Check File path
            file_or_dir_path.parent.mkdir(parents=True, exist_ok=True)
        else:  # Check directory
            file_or_dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_file_reading(path: Path, error_message: str) -> None:
        """Raises a FileNotFoundError if an expected input path does not exist."""
        if not path.exists():
            raise FileNotFoundError(f"{error_message}: {path.resolve()}")  # To be handled
