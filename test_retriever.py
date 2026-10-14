from pathlib import Path
from src.utils import PathFinder
from src.lib import RsrchType
from src.retrieval import Retriever


def main():
    # 1. Initialize your PathFinder (adjust base path if needed)
    data_dir = Path("data/datasets/question.json")  # Or your specific workspace data directory
    path_finder = PathFinder(dataset=data_dir)

    # Ensure your dataset path is set in path_finder or point to it directly
    # path_finder.dataset_path = data_dir / "unanswered_questions.json"

    print("=== Testing Retriever Pipeline ===")

    # Test modes to iterate through
    modes = [RsrchType.LEXICAL, RsrchType.VECTOR, RsrchType.HYBRID]

    for mode in modes:
        print(f"\n--- Testing Mode: {mode.value} ---")
        try:
            # Initialize Retriever
            retriever = Retriever(path_finder=path_finder, mode=mode, k=5)

            # Run batch research on the dataset
            results = retriever.research_set()

            # Validate output contract and print stats
            print(f"Successfully processed {len(results.search_results)} questions.")
            if results.search_results:
                first_res = results.search_results[0]
                print(f"Sample Question: {first_res.question}")
                print(f"Retrieved {len(first_res.retrieved_sources)} sources for top-1.")
                for src in first_res.retrieved_sources:
                    print(f"  -> {src.file_path} (chars {src.first_character_index}-{src.last_character_index})")

        except Exception as e:
            print(f"Error encountered in {mode.value} mode: {e}")


if __name__ == "__main__":
    main()