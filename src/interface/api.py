# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

"""FastAPI routes exposing indexing, search, answer, and evaluation commands."""

import re
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pathlib import Path

from src.index import Indexer
from src.retrieval import Engine
from src.lib import InterfaceIndex, InterfaceQuery, InterfaceEvaluate, InterfaceDatasetSearch, InterfaceDatasetAnswer
from src.lib import StuSrchRes, StuSrchResAns, MinSrchRes, MinAns, RsrchType


app = FastAPI()


@app.post("/api/evaluate", response_class=PlainTextResponse)
def evaluate(payload: InterfaceEvaluate) -> str:
    """Run evaluation from saved search results against a dataset.

    Args:
        payload: Evaluation inputs including results path and dataset path.

    Returns:
        Plain-text evaluation report with ANSI escapes removed.
    """
    engine = Engine(
        student_search_results_path=Path(payload.student_search_results_path),
        dataset_path=Path(payload.dataset_path)
    )
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    evaluation = ansi_escape.sub('', engine.evaluate())
    return evaluation


# LEXICAL COMMANDS
@app.post("/api/v1/index")
def index(payload: InterfaceIndex) -> None:
    """Build or update the lexical index.

    Args:
        payload: Indexing configuration including chunk size.

    """
    indexer = Indexer(max_chunk_size=payload.max_chunk_size)
    indexer.index()


@app.post("/api/v1/purge_index")
def purge_index() -> None:
    """Delete the lexical index.

    """
    engine = Engine(mode=RsrchType.LEXICAL)
    engine.purge_index()


@app.post("/api/v1/search", response_model=MinSrchRes)
def search(payload: InterfaceQuery) -> MinSrchRes:
    """Run a single lexical search query.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal search results payload.
    """
    engine = Engine(user_query=payload.query, k=payload.k)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset", response_model=StuSrchRes)
def search_dataset(payload: InterfaceDatasetSearch) -> StuSrchRes:
    """Run lexical search for a whole dataset.

    Args:
        payload: Dataset path, output directory, and retrieval count.

    Returns:
        Structured dataset search results.
    """
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k
    )
    return engine.run_set_search()


@app.post("/api/v1/answer", response_model=MinAns)
def answer(payload: InterfaceQuery) -> MinAns:
    """Generate a single lexical answer from query context.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal answer payload.
    """
    engine = Engine(user_query=payload.query, k=payload.k)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset", response_model=StuSrchResAns)
def answer_dataset(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    """Generate lexical answers for dataset search results.

    Args:
        payload: Search-results path and output directory.

    Returns:
        Structured dataset answer payload.
    """
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
    )
    return engine.run_set_answer()


# SEMMANTIC COMMANDS
@app.post("/api/v1/index_semantic")
def index_semantic(payload: InterfaceIndex) -> None:
    """Build or update the semantic index.

    Args:
        payload: Indexing configuration including chunk size.

    """
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.VECTOR)
    indexer.index()


@app.post("/api/v1/purge_index_semantic")
def purge_index_semantic() -> None:
    """Delete the semantic index.

    """
    engine = Engine(mode=RsrchType.VECTOR)
    engine.purge_index()


@app.post("/api/v1/search_semantic", response_model=MinSrchRes)
def search_semantic(payload: InterfaceQuery) -> MinSrchRes:
    """Run a single semantic search query.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal search results payload.
    """
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset_semantic", response_model=StuSrchRes)
def search_dataset_semantic(payload: InterfaceDatasetSearch) -> StuSrchRes:
    """Run semantic search for a whole dataset.

    Args:
        payload: Dataset path, output directory, and retrieval count.

    Returns:
        Structured dataset search results.
    """
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_set_search()


@app.post("/api/v1/answer_semantic", response_model=MinAns)
def answer_semantic(payload: InterfaceQuery) -> MinAns:
    """Generate a single semantic answer from query context.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal answer payload.
    """
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_semantic", response_model=StuSrchResAns)
def answer_dataset_semantic(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    """Generate semantic answers for dataset search results.

    Args:
        payload: Search-results path and output directory.

    Returns:
        Structured dataset answer payload.
    """
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
        mode=RsrchType.VECTOR)
    return engine.run_set_answer()


# HYBRID COMMANDS
@app.post("/api/v1/index_hybrid")
def index_hybrid(payload: InterfaceIndex) -> None:
    """Build or update the hybrid index.

    Args:
        payload: Indexing configuration including chunk size.

    """
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.HYBRID)
    indexer.index()


@app.post("/api/v1/purge_index_hybrid")
def purge_index_hybrid() -> None:
    """Delete the hybrid index.

    """
    engine = Engine(mode=RsrchType.HYBRID)
    engine.purge_index()


@app.post("/api/v1/search_hybrid", response_model=MinSrchRes)
def search_hybrid(payload: InterfaceQuery) -> MinSrchRes:
    """Run a single hybrid search query.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal search results payload.
    """
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset_hybrid", response_model=StuSrchRes)
def search_dataset_hybrid(payload: InterfaceDatasetSearch) -> StuSrchRes:
    """Run hybrid search for a whole dataset.

    Args:
        payload: Dataset path, output directory, and retrieval count.

    Returns:
        Structured dataset search results.
    """
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_set_search()


@app.post("/api/v1/answer_hybrid", response_model=MinAns)
def answer_hybrid(payload: InterfaceQuery) -> MinAns:
    """Generate a single hybrid answer from query context.

    Args:
        payload: Query text and retrieval count.

    Returns:
        Minimal answer payload.
    """
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_hybrid", response_model=StuSrchResAns)
def answer_dataset_hybrid(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    """Generate hybrid answers for dataset search results.

    Args:
        payload: Search-results path and output directory.

    Returns:
        Structured dataset answer payload.
    """
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
        mode=RsrchType.HYBRID)
    return engine.run_set_answer()
