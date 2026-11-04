# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
import shutil
from pathlib import Path

from src.retrieval import Oracle, Retriever, Evaluator, EngineError
from src.utils import PathFinder
from src.lib import RsrchType, Tc, ErrType, MinSrchRes, MinAns, StuSrchRes, StuSrchResAns, DocSrc


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
        self.k: int = k
        if self.k < 1:
            print(EngineError(ErrType.WRN, ValueError("'k' must be greater than 1, default to 10")))
            self.k = 10
        self.save_directory: Path | None = save_directory
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

    def run_single_search(self) -> MinSrchRes:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        to_print: str = f"\n{Tc.ylw}[SINGLE RESEARCH]{Tc.clr}\n"

        if results.retrieved_sources:
            for min_src in results.retrieved_sources:
                to_print += (
                    f"{min_src.file_path} - "
                    f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                    f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]\n"
                )
        else:
            to_print += f"{Tc.ylw}No relevant matches found for query{Tc.clr}:\n '{self.user_query}'\n"

        print(to_print)
        return results

    def run_single_answer(self) -> MinAns:
        assert isinstance(self.user_query, str)
        results: MinSrchRes = self.retriever.research(None, self.user_query)
        answer: MinAns = self.oracle.answer(results)
        to_print: str = f"\n{Tc.org}[SINGLE ANSWER]{Tc.clr}\n"

        if results.retrieved_sources and self.retriever.null_score is False:
            for min_src in answer.retrieved_sources:
                to_print += (
                    f"{min_src.file_path} - "
                    f"[{Tc.cyn}{min_src.first_character_index}{Tc.clr} : "
                    f"{Tc.cyn}{min_src.last_character_index}{Tc.clr}]\n"
                )
        else:
            to_print += f"{Tc.ylw}No relevant matches found for query{Tc.clr}:\n '{self.user_query}'\n"
        to_print += f"\n{Tc.org}LLM Answer{Tc.clr}: {answer.answer}\n"

        print(to_print)
        return answer

    def run_set_search(self) -> StuSrchRes:
        result: StuSrchRes = self.retriever.research_set()
        assert isinstance(self.path_finder.save_dir, Path)
        assert isinstance(self.path_finder.dataset_path, Path)
        output_file = self.path_finder.save_dir / self.path_finder.dataset_path.name
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=4))
        return result

    def run_set_answer(self) -> StuSrchResAns:
        answer: StuSrchResAns = self.oracle.answer_set()
        assert isinstance(self.path_finder.save_dir, Path)
        assert isinstance(self.path_finder.student_search_results_path, Path)
        output_file = self.path_finder.save_dir / self.path_finder.student_search_results_path.name
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer.model_dump_json(indent=4))
        return answer

    def evaluate(self) -> str:
        self.evaluator.run_evaluation()
        print(self.evaluator)
        return self.evaluator.evaluation_str

    def purge_index(self) -> None:
        index_folder: Path = Path()
        rag_state_file: Path = Path()

        match self.mode:
            case RsrchType.LEXICAL:
                index_folder = self.path_finder.bm25_dir
                rag_state_file = self.path_finder.rag_state_bm25_path
                self._remove_data(index_folder, rag_state_file)
            case RsrchType.VECTOR:
                index_folder = self.path_finder.vector_dir
                rag_state_file = self.path_finder.rag_state_vector_path
                self._remove_data(index_folder, rag_state_file)
            case RsrchType.HYBRID:
                self._remove_data(self.path_finder.processed_dir)
                self._remove_data(self.path_finder.state_dir)

    @staticmethod
    def _remove_data(folder: Path, rag_file: Path | None = None) -> None:
        try:
            if folder.exists():
                shutil.rmtree(folder)
            if rag_file and rag_file.exists():
                rag_file.unlink(missing_ok=True)
        except Exception as e:
            raise EngineError(ErrType.CRIT, e)
        pass

    def _load_doc_store(self) -> None:
        if self.path_finder.docsrc_path.exists():
            with open(self.path_finder.docsrc_path, "r", encoding="utf-8") as f:
                raw_docs: list[dict] = json.load(f)

            self.docsrc_store = {
                item["id"]: DocSrc.model_validate(item)
                for item in raw_docs
            }
