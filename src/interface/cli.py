# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.lib import RsrchType
from src.index import Indexer
from src.retrieval import Engine


class RAGCLI:
    def __init__(self):
        pass

    def index(self, max_chunk_size: int = 2000):
        """index datasets"""

        indexer = Indexer(max_chunk_size=max_chunk_size)
        indexer.index()
        pass

    def search(self, query: str, k: int):
        """single search"""

        engine = Engine(mode=RsrchType.LEXICAL, user_query=query, k=k)
        engine.run_single_search()

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        """search dataset"""

        engine = Engine(
            mode=RsrchType.LEXICAL,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    def answer(self, query: str, k: int):
        """single answer"""

        engine = Engine(mode=RsrchType.LEXICAL, user_query=query, k=k)
        engine.run_single_answer()

    def answer_dataset(self, student_search_result_path: str, save_directory: str):
        """answer dataset"""

        engine = Engine(
            mode=RsrchType.LEXICAL,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    def evaluate(self, student_search_result_path: str, dataset_path: str):
        """compare results"""
        pass
