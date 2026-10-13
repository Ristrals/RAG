import chromadb
from pathlib import Path

# Connect to the local vector directory
vector_dir = Path("data/processed/vector")
client = chromadb.PersistentClient(path=str(vector_dir))
collections = client.list_collections()
print(f"Found collections in vector DB: {[c.name for c in collections]}")

for col in collections:
    print(f"Collection '{col.name}' contains {col.count()} embedded chunks.")