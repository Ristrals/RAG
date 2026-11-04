# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

from src.utils import PathFinder
from src.lib import (
    Tc, ErrType, GrndTruthDs, GrndTruthQ, StuSrchRes, StuSrchResAns, MinSrchRes
)
from src.retrieval import EvaluatorError


class Evaluator:
    """Evaluate student retrieval/answer outputs against ground truth.

    Attributes:
        path_finder: Path helper exposing dataset and results locations.
        ground_truths: Parsed ground-truth dataset.
        student_results: Parsed student results (search or answer mode).
        is_answer_eval: True when evaluating answer payloads.
        k: Configured retrieval count.
        total_response: Total evaluated questions.
        valid_response: Number of validated matches.
        evaluation_str: Human-readable evaluation output.
    """

    def __init__(self, path_finder: PathFinder, k: int) -> None:
        """Initialize evaluator state.

        Args:
            path_finder: Path helper exposing required files.
            k: Retrieval count used for evaluation context.

        """
        self.path_finder = path_finder
        self.ground_truths: GrndTruthDs | None = None
        self.student_results: StuSrchRes | StuSrchResAns | None = None
        self.is_answer_eval: bool = False
        self.k = k
        self.total_response: int = 0
        self.valid_response: int = 0
        self.evaluation_str: str = ""

    def __str__(self) -> str:
        """Return the formatted evaluation summary.

        Returns:
            Evaluation summary string.
        """
        return self.evaluation_str

    def run_evaluation(self) -> None:
        """Run full evaluation pipeline and build summary text.

        """
        try:
            assert isinstance(self.path_finder.student_search_results_path, Path)
            with open(self.path_finder.student_search_results_path, "r", encoding="utf-8") as f:
                student_data = json.load(f)
            if "answers" in student_data or any("answer" in item for item in student_data.get("search_results", [])):
                self.student_results = StuSrchResAns.model_validate(student_data)
                self.is_answer_eval = True
            else:
                self.student_results = StuSrchRes.model_validate(student_data)
                self.is_answer_eval = False
        except Exception as e:
            raise EvaluatorError(ErrType.CRIT, e, 0)

        try:
            assert isinstance(self.path_finder.dataset_path, Path)
            with open(self.path_finder.dataset_path, "r", encoding="utf-8") as f:
                gt_data = json.load(f)
                self.ground_truths = GrndTruthDs.model_validate(gt_data)
        except Exception as e:
            raise EvaluatorError(ErrType.CRIT, e, 1)

        self.evaluation_str += (
            f"\n{Tc.mag}[EVALUATION]{Tc.clr} Loaded evaluation mode: {'Answer' if self.is_answer_eval else 'Search'}\n")

        assert isinstance(self.student_results, StuSrchRes | StuSrchResAns)
        for question in self.student_results.search_results:
            self.total_response += 1
            ground_truth: GrndTruthQ | None = self._get_ground_truth(question.question_id)
            if ground_truth:
                match self._evaluate(question, ground_truth):
                    case "valid":
                        self.evaluation_str += (
                            f"{Tc.ylw}QUESTION{Tc.clr} {question.question_id} -> "
                            f"Overlap confirmed [{Tc.grn}VALIDATED{Tc.clr}]\n")
                    case "no_overlap":
                        self.evaluation_str += (
                            f"{Tc.ylw}QUESTION{Tc.clr} {question.question_id} -> "
                            f"No index overlap [{Tc.org}FAILED{Tc.clr}]\n")
                    case "no_match":
                        self.evaluation_str += (
                            f"{Tc.ylw}QUESTION{Tc.clr} {question.question_id} -> "
                            f"No matching source file [{Tc.red}FAILED{Tc.clr}]\n")
            else:
                self.evaluation_str += (
                    f"{Tc.ylw}QUESTION{Tc.clr} {question.question_id} -> "
                    f"Matching question ID not found [{Tc.red}MISSING{Tc.clr}]\n")

        self._calculate_accuracy()

    def _get_ground_truth(self, question_id: str) -> GrndTruthQ | None:
        """Return ground-truth entry matching a question id.

        Args:
            question_id: Question identifier to resolve.

        Returns:
            Matching ground-truth question or None.
        """
        assert isinstance(self.ground_truths, GrndTruthDs)
        return next((gtq for gtq in self.ground_truths.rag_questions if gtq.question_id == question_id), None)

    def _evaluate(self, question: MinSrchRes, ground_truth: GrndTruthQ) -> str:
        """Compare retrieved sources against one ground-truth entry.

        Args:
            question: Student search result for one question.
            ground_truth: Reference ground-truth question entry.

        Returns:
            Evaluation status string: ``valid``, ``no_overlap``, or ``no_match``.
        """
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
        """Check whether two character ranges overlap.

        Args:
            start1: First range start offset.
            end1: First range end offset.
            start2: Second range start offset.
            end2: Second range end offset.

        Returns:
            True when ranges overlap, otherwise False.
        """
        return max(start1, start2) <= min(end1, end2)

    def _calculate_accuracy(self) -> None:
        """Compute and append evaluation accuracy summary.

        """
        if self.total_response == 0:
            accuracy = 0.0
        else:
            accuracy = (self.valid_response / self.total_response) * 100

        self.evaluation_str += (
            f"\n{Tc.ylw}\n[EVALUATION SUMMARY]{Tc.clr}\n"
            f"Total Evaluated: {self.total_response}\n"
            f"Valid Matches:   {self.valid_response}\n"
            f"Accuracy Rate:   {Tc.grn}{accuracy:.2f}%{Tc.clr}")
