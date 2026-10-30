# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import re
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pathlib import Path

from src.index import Indexer
from src.retrieval import Engine
from src.lib import APIIndex, APIQuery, APIEvaluate, APIDatasetSearch, APIDatasetAnswer
from src.lib import StuSrchRes, StuSrchResAns, MinSrchRes, MinAns, RsrchType


app = FastAPI()


@app.post("/api/evaluate", response_class=PlainTextResponse)
def evaluate(payload: APIEvaluate) -> str:
    engine = Engine(
        student_search_results_path=Path(payload.student_result_path),
        dataset_path=Path(payload.ground_truth_path)
    )
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    evaluation = ansi_escape.sub('', engine.evaluate())
    return evaluation

# LEXICAL COMMANDS
@app.post("/api/v1/index")
def index(payload: APIIndex):
    indexer = Indexer(max_chunk_size=payload.max_chunk_size)
    indexer.index()

@app.post("/api/v1/search", response_model=MinSrchRes)
def search(payload: APIQuery):
    engine = Engine(user_query=payload.question, k=payload.k)
    return engine.run_single_search()

@app.post("/api/v1/search_dataset", response_model=StuSrchRes)
def search_dataset(payload: APIDatasetSearch):
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory_path),
        k=payload.k
    )
    return engine.run_set_search()

@app.post("/api/v1/answer", response_model=MinAns)
def answer(payload: APIQuery):
    engine = Engine(user_query=payload.question, k=payload.k)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset", response_model=StuSrchResAns)
def answer_dataset(payload: APIDatasetAnswer):
    engine = Engine(
        student_search_results_path=Path(payload.student_result_path),
        save_directory=Path(payload.save_directory_path),
    )
    return engine.run_set_answer()

# SEMMANTIC COMMANDS
@app.post("/api/v1/index_semantic")
def index_semantic(payload: APIIndex):
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.VECTOR)
    indexer.index()

@app.post("/api/v1/search_semantic", response_model=MinSrchRes)
def search_semantic(payload: APIQuery):
    engine = Engine(
        user_query=payload.question,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_set_search()

@app.post("/api/v1/search_dataset_semantic", response_model=StuSrchRes)
def search_dataset_semantic(payload: APIDatasetSearch):
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory_path),
        k=payload.k,
        mode = RsrchType.VECTOR)
    return engine.run_set_search()

@app.post("/api/v1/answer_semantic", response_model=MinAns)
def answer_semantic(payload: APIQuery):
    engine = Engine(
        user_query=payload.question,
        k=payload.k,
        mode=RsrchType.VECTOR)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_semantic", response_model=StuSrchResAns)
def answer_dataset_semantic(payload: APIDatasetAnswer):
    engine = Engine(
        student_search_results_path=Path(payload.student_result_path),
        save_directory=Path(payload.save_directory_path),
        mode=RsrchType.VECTOR)
    return engine.run_set_answer()

# HYBRID COMMANDS
@app.post("/api/v1/index_hybrid")
def index_hybrid(payload: APIIndex):
    indexer = Indexer(
        max_chunk_size=payload.max_chunk_size,
        mode=RsrchType.HYBRID)
    indexer.index()

@app.post("/api/v1/search_hybrid", response_model=MinSrchRes)
def search_hybrid(payload: APIQuery):
    engine = Engine(
        user_query=payload.question,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_set_search()

@app.post("/api/v1/search_dataset_hybrid", response_model=StuSrchRes)
def search_dataset_hybrid(payload: APIDatasetSearch):
    engine = Engine(
        dataset_path=Path(payload.dataset_path),
        save_directory=Path(payload.save_directory_path),
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_set_search()

@app.post("/api/v1/answer_hybrid", response_model=MinAns)
def answer_hybrid(payload: APIQuery):
    engine = Engine(
        user_query=payload.question,
        k=payload.k,
        mode=RsrchType.HYBRID)
    return engine.run_single_answer()


@app.post("/api/v1/answer_dataset_hybrid", response_model=StuSrchResAns)
def answer_dataset_hybrid(payload: APIDatasetAnswer):
    engine = Engine(
        student_search_results_path=Path(payload.student_result_path),
        save_directory=Path(payload.save_directory_path),
        mode=RsrchType.HYBRID)
    return engine.run_set_answer()