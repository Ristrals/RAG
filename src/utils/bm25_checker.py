import json
from pathlib import Path
# A quick check that the vocab and parameters exist and are readable
vocab_path = Path("data/processed/bm25_index/vocab.index.json")
if vocab_path.exists():
    with open(vocab_path, "r") as f:
        vocab = json.load(f)
    print(f"BM25 Vocab loaded successfully with {len(vocab)} unique terms.")