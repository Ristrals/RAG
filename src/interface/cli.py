# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import uvicorn
from pathlib import Path

from src.interface import CommandName
from src.interface import validate_args
from src.lib import RsrchType
from src.index import Indexer
from src.retrieval import Engine
from src.utils import PathFinder
from src.lib import InterfaceIndex, InterfaceQuery, InterfaceEvaluate, InterfaceDatasetSearch, InterfaceDatasetAnswer


class RAGCLI:
    """Command-line interface wrapper for indexing and retrieval workflows."""

    def serve(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
        """Launch the local HTTP API server.

        Args:
            host: Network host for the API server.
            port: TCP port for the API server.
            reload: Whether to enable auto-reload for development.

        """

        print(f"Starting RAG API server at http://{host}:{port}")
        uvicorn.run("src.interface.api:app", host=host, port=port, reload=reload)

    def data(self) -> None:
        """Creates base data folders.

        """

        pathfinder = PathFinder()
        pathfinder.secure_index_directories()

    @validate_args(InterfaceEvaluate, CommandName.EVAL)
    def evaluate(self, student_search_results_path: str, dataset_path: str) -> None:
        """Evaluate saved search results against a reference dataset.

        Args:
            student_search_results_path: Path to previously saved search results.
            dataset_path: Path to the reference dataset.

        """

        engine = Engine(
            student_search_results_path=Path(student_search_results_path),
            dataset_path=Path(dataset_path)
        )
        engine.evaluate()

    # LEXICAL COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index(self, max_chunk_size: int = 2000) -> None:
        """Build or update the lexical index.

        Args:
            max_chunk_size: Maximum number of characters per chunk.

        """

        indexer = Indexer(max_chunk_size=max_chunk_size)
        indexer.index()

    def purge_index(self) -> None:
        """Delete lexical index artifacts.

        """

        engine = Engine(mode=RsrchType.LEXICAL)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search(self, query: str, k: int) -> None:
        """Run a single lexical search query.

        Args:
            query: User query string.
            k: Number of results to retrieve.

        """

        engine = Engine(user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset(self, dataset_path: str, k: int, save_directory: str) -> None:
        """Run lexical search across a full dataset.

        Args:
            dataset_path: Path to the input dataset.
            k: Number of results to retrieve per query.
            save_directory: Output directory for generated results.

        """

        engine = Engine(
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def answer(self, query: str, k: int) -> None:
        """Generate a single lexical answer.

        Args:
            query: User query string.
            k: Number of context results to retrieve.

        """

        engine = Engine(user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceDatasetAnswer, CommandName.ANS_DS)
    def answer_dataset(self, student_search_result_path: str, save_directory: str) -> None:
        """Generate lexical answers for a dataset of search results.

        Args:
            student_search_result_path: Path to dataset search results.
            save_directory: Output directory for generated answers.

        """

        engine = Engine(
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # SEMANTIC COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index_semantic(self, max_chunk_size: int = 2000) -> None:
        """Build or update the semantic index.

        Args:
            max_chunk_size: Maximum number of characters per chunk.

        """

        indexer = Indexer(max_chunk_size=max_chunk_size, mode=RsrchType.VECTOR)
        indexer.index()

    def purge_index_semantic(self) -> None:
        """Delete semantic index artifacts.

        """

        engine = Engine(mode=RsrchType.VECTOR)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search_semantic(self, query: str, k: int) -> None:
        """Run a single semantic search query.

        Args:
            query: User query string.
            k: Number of results to retrieve.

        """

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset_semantic(self, dataset_path: str, k: int, save_directory: str) -> None:
        """Run semantic search across a full dataset.

        Args:
            dataset_path: Path to the input dataset.
            k: Number of results to retrieve per query.
            save_directory: Output directory for generated results.

        """

        engine = Engine(
            mode=RsrchType.VECTOR,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def answer_semantic(self, query: str, k: int) -> None:
        """Generate a single semantic answer.

        Args:
            query: User query string.
            k: Number of context results to retrieve.

        """

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceDatasetAnswer, CommandName.ANS_DS)
    def answer_dataset_semantic(self, student_search_result_path: str, save_directory: str) -> None:
        """Generate semantic answers for a dataset of search results.

        Args:
            student_search_result_path: Path to dataset search results.
            save_directory: Output directory for generated answers.

        """

        engine = Engine(
            mode=RsrchType.VECTOR,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # HYBRID COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index_hybrid(self, max_chunk_size: int = 2000) -> None:
        """Build or update the hybrid index.

        Args:
            max_chunk_size: Maximum number of characters per chunk.

        """

        indexer = Indexer(max_chunk_size=max_chunk_size, mode=RsrchType.HYBRID)
        indexer.index()

    def purge_index_hybrid(self) -> None:
        """Delete hybrid index artifacts.

        """

        engine = Engine(mode=RsrchType.HYBRID)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search_hybrid(self, query: str, k: int) -> None:
        """Run a single hybrid search query.

        Args:
            query: User query string.
            k: Number of results to retrieve.

        """

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset_hybrid(self, dataset_path: str, k: int, save_directory: str) -> None:
        """Run hybrid search across a full dataset.

        Args:
            dataset_path: Path to the input dataset.
            k: Number of results to retrieve per query.
            save_directory: Output directory for generated results.

        """

        engine = Engine(
            mode=RsrchType.HYBRID,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def answer_hybrid(self, query: str, k: int) -> None:
        """Generate a single hybrid answer.

        Args:
            query: User query string.
            k: Number of context results to retrieve.

        """

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceDatasetAnswer, CommandName.ANS_DS)
    def answer_dataset_hybrid(self, student_search_result_path: str, save_directory: str) -> None:
        """Generate hybrid answers for a dataset of search results.

        Args:
            student_search_result_path: Path to dataset search results.
            save_directory: Output directory for generated answers.

        """

        engine = Engine(
            mode=RsrchType.HYBRID,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()
