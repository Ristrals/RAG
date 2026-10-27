# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

from src.utils import PathFinder
from src.lib import (
    Tc, GrndTruthDs, GrndTruthQ, StuSrchRes,StuSrchResAns, MinSrchRes
)


class Evaluator:
    def __init__(self, path_finder: PathFinder, k: int) -> None:
        self.path_finder = path_finder
        self.ground_truths: GrndTruthDs | None = None
        self.student_results: StuSrchRes | StuSrchResAns | None = None
        self.is_answer_eval: bool = False
        self.k = k
        self.total_response: int = 0
        self.valid_response: int = 0


    def run_evaluation(self):
        assert isinstance(self.path_finder.student_search_results_path, Path)
        with open(self.path_finder.student_search_results_path, "r", encoding="utf-8") as f:
            student_data = json.load(f)
        if "answers" in student_data or any("answer" in item for item in student_data.get("search_results", [])):
            self.student_results = StuSrchResAns.model_validate(student_data)
            self.is_answer_eval = True
        else:
            self.student_results = StuSrchRes.model_validate(student_data)
            self.is_answer_eval = False

        assert isinstance(self.path_finder.dataset_path, Path)
        with open(self.path_finder.dataset_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
            self.ground_truths: GrndTruthDs = GrndTruthDs.model_validate(gt_data)

        print(f"\n{Tc.mag}[EVALUATION]{Tc.clr} Loaded evaluation mode: {'Answer' if self.is_answer_eval else 'Search'}")

        assert isinstance(self.student_results, StuSrchRes | StuSrchResAns)
        for question in self.student_results.search_results:
            self.total_response += 1
            ground_truth: GrndTruthQ | None = self._get_ground_truth(question.question_id)
            if ground_truth:
                match self._evaluate(question, ground_truth):
                    case "valid":
                        print(f"{Tc.ylw}QUESTION{Tc.clr} '{question.question}' -> Overlap confirmed [{Tc.grn}VALIDATED{Tc.clr}]")
                    case "no_overlap":
                        print(f"{Tc.ylw}QUESTION{Tc.clr} '{question.question}' -> No index overlap [{Tc.org}FAILED{Tc.clr}]")
                    case "no_match":
                        print(f"{Tc.ylw}QUESTION{Tc.clr} '{question.question}' -> No matching source file [{Tc.red}FAILED{Tc.clr}]")
            else:
                print(f"{Tc.ylw}QUESTION{Tc.clr} {question.question_id} -> Matching question ID not found [{Tc.red}MISSING{Tc.clr}]")

        self._calculate_accuracy()

    def _get_ground_truth(self, question_id: str) -> GrndTruthQ | None:
        assert isinstance(self.ground_truths, GrndTruthDs)
        return next((gtq for gtq in self.ground_truths.rag_questions if gtq.question_id == question_id), None)

    def _evaluate(self, question: MinSrchRes, ground_truth: GrndTruthQ) -> str:
        valid_minimal_source = ground_truth.sources[0]
        for result in question.retrieved_sources:
            if result.file_path == valid_minimal_source.file_path:
                if self._ranges_overlap(
                    result.first_character_index,
                    result.last_character_index,
                    valid_minimal_source.first_character_index,
                    valid_minimal_source.last_character_index,
                ):
                    self.valid_response += 1
                    return "valid"
                else:
                    return "no_overlap"
        return "no_match"

    def _ranges_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        return max(start1, start2) <= min(end1, end2)

    def _calculate_accuracy(self):
        if self.total_response == 0:
            accuracy = 0.0
        else:
            accuracy = (self.valid_response / self.total_response) * 100

        print(f"\n{Tc.ylw}\n[EVALUATION SUMMARY]{Tc.clr}")
        print(f"Total Evaluated: {self.total_response}")
        print(f"Valid Matches:   {self.valid_response}")
        print(f"Accuracy Rate:   {Tc.grn}{accuracy:.2f}%{Tc.clr}")
