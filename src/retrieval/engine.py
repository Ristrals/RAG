# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

from src.retrieval import Oracle, Retriever, Evaluator
from src.utils import PathFinder
from src.lib import RsrchType, Tc, MinSrchRes, MinAns, StuSrchRes, StuSrchResAns, DocSrc


class Engine:
    def __init__(
        self, mode: RsrchType = RsrchType.LEXICAL,
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
        self.path_finder: PathFinder = PathFinder(
            save_directory=save_directory,
            dataset_path=dataset_path,
            student_search_results_path=student_search_results_path,)
        self.docsrc_store: dict[str, DocSrc] = {}
        self._load_doc_store()
        self.retriever: Retriever = Retriever(self.path_finder, self.mode, self.docsrc_store, self.k)
        self.oracle: Oracle = Oracle(self.path_finder, self.docsrc_store, self.k)
        self.evaluator: Evaluator = Evaluator(self.path_finder, self.k)

    def run_single_search(self) -> None:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        to_print: str = f"\n{Tc.ylw}[SINGLE RESEARCH]{Tc.clr}\n"

        for min_src in results.retrieved_sources:
            to_print += (
                f"{min_src.file_path} - "
                f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]\n"
            )

        print(to_print)

    def run_single_answer(self) -> None:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        answer: MinAns = self.oracle.answer(results)

        to_print: str = f"\n{Tc.org}[SINGLE ANSWER]{Tc.clr}\n"
        for min_src in answer.retrieved_sources:
            to_print += (
                f"{min_src.file_path} - "
                f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]\n"
            )
        to_print += f"{Tc.org}LLM Answer{Tc.clr}: {answer.answer}\n"

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

    def evaluate(self) -> None:
        self.evaluator.run_evaluation()

    def _load_doc_store(self) -> None:
        if self.path_finder.docsrc_path.exists():
            with open(self.path_finder.docsrc_path, "r", encoding="utf-8") as f:
                raw_docs: list[dict] = json.load(f)

            self.docsrc_store = {
                item["id"]: DocSrc.model_validate(item)
                for item in raw_docs
            }