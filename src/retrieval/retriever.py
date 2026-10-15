# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
import uuid
from pathlib import Path

from src.lib import (
    MinSrc,
    RagDataset,
    MinSrchRes,
    StuSrchRes,
    RsrchType
)
from src.operator import BM25Op, VectorOp
from src.utils import PathFinder


class Retriever:
    _C = 60

    def __init__(
        self, path_finder: PathFinder,
        mode: RsrchType,
        docsrc_store: dict[str, dict],
        k: int = 10,
    ) -> None:

        self.path_finder = path_finder
        self.mode = mode
        self.k = k
        self.docsrc_store: dict[str, dict] = docsrc_store

        if mode == RsrchType.LEXICAL or mode == RsrchType.HYBRID:
            self.bm25_op = BM25Op()
            self.bm25_op.load(self.path_finder.bm25_dir)
        if mode == RsrchType.VECTOR or mode == RsrchType.HYBRID:
            self.vector_op = VectorOp()
            self.vector_op.load(self.path_finder.vector_dir)

    def research(self, question_id: str | None, question_text: str) -> MinSrchRes:
        raw_results: list[tuple[str, float]] = []
        retrieved_sources: list[MinSrc] = []

        match self.mode:
            case RsrchType.LEXICAL:
                raw_results = self.bm25_op.search(question_text, self.path_finder.bm25_dir, k=self.k)
            case RsrchType.VECTOR:
                raw_results = self.vector_op.search(question_text, self.path_finder.vector_dir, k=self.k)
            case RsrchType.HYBRID:
                raw_bm25_res = self.bm25_op.search(question_text, self.path_finder.bm25_dir, k=self.k)
                raw_vector_res = self.vector_op.search(question_text, self.path_finder.vector_dir, k=self.k)
                raw_results = self._hybrid_research_calculation(raw_bm25_res, raw_vector_res)

        for doc_id, score in raw_results:
            doc_data = self.docsrc_store.get(doc_id, {})
            retrieved_sources.append(
                MinSrc(
                    file_path=doc_data.get("file_path", ""),
                    first_character_index=doc_data.get("first_character_index", 0),
                    last_character_index=doc_data.get("last_character_index", 0)
                )
            )

        return MinSrchRes(
            question_id=question_id if question_id else str(uuid.uuid4()),
            question=question_text,
            retrieved_sources=retrieved_sources
        )

    def research_set(self) -> StuSrchRes:
        try:
            assert isinstance(self.path_finder.dataset_path, Path)
            self.path_finder.validate_file_reading(self.path_finder.dataset_path, "Dataset not found")
            with open(self.path_finder.dataset_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                dataset: RagDataset = RagDataset.model_validate(raw_data)
        except Exception as e:
            raise e # TOBBE HANDLED TO VERIFY PROPER JSON SCHEMA

        student_search_results: list[MinSrchRes] = []
        for query in dataset.rag_questions:
            student_search_results.append(self.research(query.question_id, query.question))
        return StuSrchRes(
            search_results=student_search_results,
            k=self.k
        )

    def _hybrid_research_calculation(
            self, bm25_res: list[tuple[str, float]],
            vector_res: list[tuple[str, float]]
    ) -> list[tuple[str, float]]:
        rrf_scores: dict[str, float] = {}

        for rank, (doc_id, _) in enumerate(bm25_res, start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (self._C + rank)
        for rank, (doc_id, _) in enumerate(vector_res, start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (self._C + rank)

        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_docs[:self.k]
