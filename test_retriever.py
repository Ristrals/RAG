# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path
from src.retrieval import Retriever
from src.utils import PathFinder
from src.lib import RsrchType


def test_retriever():
    print("=== Testing Retriever Pipeline ===")

    path_finder = PathFinder()

    # Load the document store index just like the Engine does
    index_path = path_finder.processed_dir / "std_index.json"
    if not index_path.exists():
        print(f"Error: Index file not found at {index_path}. Run indexing first!")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)
        docsrc_store = {doc["id"]: doc for doc in raw_docs}

    modes = [RsrchType.LEXICAL, RsrchType.VECTOR, RsrchType.HYBRID]

    for mode in modes:
        print(f"\n--- Testing Mode: {mode.value} ---")
        try:
            # Pass all required arguments including docsrc_store
            retriever = Retriever(path_finder=path_finder, mode=mode, docsrc_store=docsrc_store, k=5)

            # Run a sample test query
            test_query = "How to configure OpenAI server?"
            result = retriever.research(question_id=None, question_text=test_query)

            print(f"Successfully retrieved {len(result.retrieved_sources)} sources for query.")
            for src in result.retrieved_sources:
                print(f" -> {src.file_path} [{src.first_character_index}:{src.last_character_index}]")

        except Exception as e:
            print(f"Error encountered in {mode.value} mode: {e}")


if __name__ == "__main__":
    test_retriever()