# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from src.index import Indexer


class RAGCLI:
    def __init__(self):
        pass

    def index(self, max_chunk_size: int = 1000):
        """index datasets"""
        indexer = Indexer(max_chunk_size=max_chunk_size)
        indexer.index()
        pass

    def search(self, query: str, k: int):
        """simple search"""
        pass

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        """search dataset"""
        pass

    def answer(self, query: str, k: int):
        """simple answer"""
        pass

    def answer_dataset(self, student_search_result_path: str, saved_directory: str):
        """answer dataset"""
        pass

    def evaluate(self, student_search_result_path: str, dataset_path: str):
        """compare results"""
        pass
