# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import uvicorn
from pathlib import Path

from src.interface import CommandName
from src.interface import validate_args
from src.lib import RsrchType
from src.index import Indexer
from src.retrieval import Engine
from src.lib import InterfaceIndex, InterfaceQuery, InterfaceEvaluate, InterfaceDatasetSearch, InterfaceDatasetAnswer


class RAGCLI:

    def serve(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
        """Launch the local HTTP API server."""

        print(f"Starting RAG API server at http://{host}:{port}")
        uvicorn.run("src.interface.api:app", host=host, port=port, reload=reload)

    @validate_args(InterfaceEvaluate, CommandName.EVAL)
    def evaluate(self, student_search_results_path: str, dataset_path: str) -> None:
        """compare results"""

        engine = Engine(
            student_search_results_path=Path(student_search_results_path),
            dataset_path=Path(dataset_path)
        )
        engine.evaluate()

    # LEXICAL COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index(self, max_chunk_size: int = 2000) -> None:
        """index datasets"""

        indexer = Indexer(max_chunk_size=max_chunk_size)
        indexer.index()

    def purge_index(self) -> None:
        """purge lexical index"""

        engine = Engine(mode=RsrchType.LEXICAL)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search(self, query: str, k: int) -> None:
        """single search"""

        engine = Engine(user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset(self, dataset_path: str, k: int, save_directory: str) -> None:
        """search dataset"""

        engine = Engine(
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def answer(self, query: str, k: int) -> None:
        """single answer"""

        engine = Engine(user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceDatasetAnswer, CommandName.ANS_DS)
    def answer_dataset(self, student_search_result_path: str, save_directory: str) -> None:
        """answer dataset"""

        engine = Engine(
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # SEMANTIC COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index_semantic(self, max_chunk_size: int = 2000) -> None:
        """index datasets"""

        indexer = Indexer(max_chunk_size=max_chunk_size, mode=RsrchType.VECTOR)
        indexer.index()

    def purge_index_semantic(self) -> None:
        """purge semantic index"""

        engine = Engine(mode=RsrchType.VECTOR)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search_semantic(self, query: str, k: int) -> None:
        """single search with hybrid context"""

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset_semantic(self, dataset_path: str, k: int, save_directory: str) -> None:
        """search dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.VECTOR,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def answer_semantic(self, query: str, k: int) -> None:
        """single answer with hybrid context"""

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceDatasetAnswer, CommandName.ANS_DS)
    def answer_dataset_semantic(self, student_search_result_path: str, save_directory: str) -> None:
        """answer dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.VECTOR,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # HYBRID COMMANDS
    @validate_args(InterfaceIndex, CommandName.IND)
    def index_hybrid(self, max_chunk_size: int = 2000) -> None:
        """index datasets"""

        indexer = Indexer(max_chunk_size=max_chunk_size, mode=RsrchType.HYBRID)
        indexer.index()

    def purge_index_hybrid(self) -> None:
        """complete index purge"""

        engine = Engine(mode=RsrchType.HYBRID)
        engine.purge_index()

    @validate_args(InterfaceQuery, CommandName.SRCH)
    def search_hybrid(self, query: str, k: int) -> None:
        """single search with hybrid context"""

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_search()

    @validate_args(InterfaceDatasetSearch, CommandName.SRCH_DS)
    def search_dataset_hybrid(self, dataset_path: str, k: int, save_directory: str) -> None:
        """search dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.HYBRID,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    @validate_args(InterfaceDatasetAnswer, CommandName.SRCH)
    def answer_hybrid(self, query: str, k: int) -> None:
        """single answer with hybrid context"""

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_answer()

    @validate_args(InterfaceQuery, CommandName.ANS_DS)
    def answer_dataset_hybrid(self, student_search_result_path: str, save_directory: str) -> None:
        """answer dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.HYBRID,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()
