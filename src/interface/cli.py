# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.lib import RsrchType
from src.index import Indexer
from src.retrieval import Engine


class RAGCLI:
    def index(self, max_chunk_size: int = 2000):
        """index datasets"""

        indexer = Indexer(max_chunk_size=max_chunk_size)
        indexer.index()

    def evaluate(self, student_search_results_path: str, dataset_path: str):
        """compare results"""

        engine = Engine(
            student_search_results_path=Path(student_search_results_path),
            dataset_path=Path(dataset_path)
        )
        engine.evaluate()

    # LEXICAL COMMANDS
    def search(self, query: str, k: int):
        """single search"""

        engine = Engine(user_query=query, k=k)
        engine.run_single_search()

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        """search dataset"""

        engine = Engine(
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    def answer(self, query: str, k: int):
        """single answer"""

        engine = Engine(user_query=query, k=k)
        engine.run_single_answer()

    def answer_dataset(self, student_search_result_path: str, save_directory: str):
        """answer dataset"""

        engine = Engine(
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # SEMMANTIC COMMANDS
    def search_vector(self, query: str, k: int):
        """single search with hybrid context"""

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_search()

    def search_dataset_vector(self, dataset_path: str, k: int, save_directory: str):
        """search dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.VECTOR,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    def answer_vector(self, query: str, k: int):
        """single answer with hybrid context"""

        engine = Engine(mode=RsrchType.VECTOR, user_query=query, k=k)
        engine.run_single_answer()

    def answer_dataser_vector(self, student_search_result_path: str, save_directory: str):
        """answer dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.VECTOR,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()

    # HYBRID COMMANDS
    def search_hybrid(self, query: str, k: int):
        """single search with hybrid context"""

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_search()

    def search_dataset_hybrid(self, dataset_path: str, k: int, save_directory: str):
        """search dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.HYBRID,
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k
        )
        engine.run_set_search()

    def answer_hybrid(self, query: str, k: int):
        """single answer with hybrid context"""

        engine = Engine(mode=RsrchType.HYBRID, user_query=query, k=k)
        engine.run_single_answer()

    def answer_dataser_hybrid(self, student_search_result_path: str, save_directory: str):
        """answer dataset with hybrid context"""

        engine = Engine(
            mode=RsrchType.HYBRID,
            student_search_results_path=Path(student_search_result_path),
            save_directory=Path(save_directory),
        )
        engine.run_set_answer()
