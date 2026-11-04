# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

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
    indexer = Indexer(max_chunk_size=payload.max_chunk_size)
    indexer.index()


@app.post("/api/v1/purge_index")
def purge_index() -> None:
    engine = Engine(mode=RsrchType.LEXICAL)
    engine.purge_index()


@app.post("/api/v1/search", response_model=MinSrchRes)
def search(payload: InterfaceQuery) -> MinSrchRes:
    engine = Engine(user_query=payload.query, k=payload.k)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset", response_model=StuSrchRes)
def search_dataset(payload: InterfaceDatasetSearch) -> StuSrchRes:
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k
    )
    return engine.run_set_search()


@app.post("/api/v1/answer", response_model=MinAns)
def answer(payload: InterfaceQuery) -> MinAns:
    engine = Engine(user_query=payload.query, k=payload.k)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset", response_model=StuSrchResAns)
def answer_dataset(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
    )
    return engine.run_set_answer()


# SEMMANTIC COMMANDS
@app.post("/api/v1/index_semantic")
def index_semantic(payload: InterfaceIndex) -> None:
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.VECTOR)
    indexer.index()


@app.post("/api/v1/purge_index_semantic")
def purge_index_semantic() -> None:
    engine = Engine(mode=RsrchType.VECTOR)
    engine.purge_index()


@app.post("/api/v1/search_semantic", response_model=MinSrchRes)
def search_semantic(payload: InterfaceQuery) -> MinSrchRes:
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset_semantic", response_model=StuSrchRes)
def search_dataset_semantic(payload: InterfaceDatasetSearch) -> StuSrchRes:
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_set_search()


@app.post("/api/v1/answer_semantic", response_model=MinAns)
def answer_semantic(payload: InterfaceQuery) -> MinAns:
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_semantic", response_model=StuSrchResAns)
def answer_dataset_semantic(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
        mode=RsrchType.VECTOR)
    return engine.run_set_answer()


# HYBRID COMMANDS
@app.post("/api/v1/index_hybrid")
def index_hybrid(payload: InterfaceIndex) -> None:
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.HYBRID)
    indexer.index()


@app.post("/api/v1/purge_index_hybrid")
def purge_index_hybrid() -> None:
    engine = Engine(mode=RsrchType.HYBRID)
    engine.purge_index()


@app.post("/api/v1/search_hybrid", response_model=MinSrchRes)
def search_hybrid(payload: InterfaceQuery) -> MinSrchRes:
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_single_search()


@app.post("/api/v1/search_dataset_hybrid", response_model=StuSrchRes)
def search_dataset_hybrid(payload: InterfaceDatasetSearch) -> StuSrchRes:
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory),
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_set_search()


@app.post("/api/v1/answer_hybrid", response_model=MinAns)
def answer_hybrid(payload: InterfaceQuery) -> MinAns:
    engine = Engine(
        user_query=payload.query,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_hybrid", response_model=StuSrchResAns)
def answer_dataset_hybrid(payload: InterfaceDatasetAnswer) -> StuSrchResAns:
    engine = Engine(
        student_search_results_path=Path(payload.student_search_result_path),
        save_directory=Path(payload.save_directory),
        mode=RsrchType.HYBRID)
    return engine.run_set_answer()
