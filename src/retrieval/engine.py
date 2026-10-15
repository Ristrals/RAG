# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

from src.retrieval import Oracle, Retriever
from src.utils import PathFinder
from src.lib import RsrchType, Tc, MinSrchRes, MinAns, StuSrchRes, StuSrchResAns


class Engine:
    def __init__(
        self, mode: RsrchType,
        user_query: str | None = None,
        save_directory: Path | None = None,
        dataset_path: Path | None = None,
        student_search_results_path: Path | None = None,
        k: int = 10,
        model_name: str = "Qwen/Qwen3-0.6B"
    ) -> None:

        self.mode: RsrchType = mode
        self.user_query: str | None = user_query
        self.k = k
        self.model_name = model_name
        self.path_finder: PathFinder = PathFinder(save_directory, dataset_path, student_search_results_path)
        self.docsrc_store: dict[str, dict] = {}
        self._load_doc_store()
        self.retriever: Retriever = Retriever(self.path_finder, self.mode, self.docsrc_store, self.k)
        self.oracle: Oracle = Oracle(self.path_finder, self.docsrc_store, self.k)

    def run_single_search(self) -> None:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        to_print: str = f"{Tc.ylw}[SINGLE RESEARCH]{Tc.clr}"

        for min_src in results.retrieved_sources:
            to_print += (
                f"{min_src.file_path} - "
                f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]"
            )

        print(to_print)

    def run_single_answer(self) -> None:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        answer: MinAns = self.oracle.answer(results)

        to_print: str = f"{Tc.org}[SINGLE ANSWER]{Tc.clr}"
        for min_src in answer.retrieved_sources:
            to_print += (
                f"{min_src.file_path} - "
                f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]"
            )
        to_print += f"{Tc.org}LLM Answer{Tc.clr}: {answer.answer}"

        print(to_print)

    def run_set_search(self) -> None:
        result: StuSrchRes = self.retriever.research_set()
        assert isinstance(self.path_finder.save_dir, Path)
        assert isinstance(self.path_finder.dataset_path, Path)
        output_file = self.path_finder.save_dir / self.path_finder.dataset_path.name
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=4))

    def run_set_answer(self) -> None:
        answer: StuSrchResAns = self.oracle.answer_set()
        assert isinstance(self.path_finder.save_dir, Path)
        assert isinstance(self.path_finder.student_search_results_path, Path)
        output_file = self.path_finder.save_dir / self.path_finder.student_search_results_path.name
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer.model_dump_json(indent=4))
        pass

    def _load_doc_store(self) -> None:
        with open(self.path_finder.processed_dir / "std_index.json", "r", encoding="utf-8") as f:
            raw_docs = json.load(f)
            self.doc_store = {doc["id"]: doc for doc in raw_docs}