# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import uuid
from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """Minimal source reference used in datasets and responses.

    Attributes:
        file_path: Source file path.
        first_character_index: Start offset in source file.
        last_character_index: End offset in source file.
    """

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """Dataset question entry without an expected answer.

    Attributes:
        question_id: Stable unique identifier for the question.
        question: Question text.
    """

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """Dataset question entry with answer and supporting sources.

    Attributes:
        sources: Source references used to justify the answer.
        answer: Expected answer text.
    """

    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Container for RAG dataset question entries."""

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """Minimal response schema for search results."""

    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Minimal response schema for generated answers."""

    answer: str


class StudentSearchResults(BaseModel):
    """Collection of search results generated for a dataset."""

    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Collection of generated answers for a dataset."""

    search_results: list[MinimalAnswer]
    k: int
