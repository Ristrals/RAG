import sqlite3
from pathlib import Path

# Define the expected path to your SQLite state directory
state_dir = Path("data/processed/lexical")
db_files = list(state_dir.glob("*.db")) if state_dir.exists() else []

print(f"Checking SQLite state directory: {state_dir.resolve()}")

if not state_dir.exists() or not db_files:
    print("[ERROR] FTS5 SQLite database not found in data/state/. (Did you run index_hybrid or index lexical?)")
else:
    for db_path in db_files:
        print(f"\nFound database: {db_path.name}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Tables found: {tables}")

            # Count rows in FTS / chunk tables
            fts_tables = [t for t in tables if "fts" in t.lower() or "chunk" in t.lower() or "doc" in t.lower()]
            for table in fts_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"Table '{table}' has {count} indexed rows.")

            conn.close()
        except Exception as e:
            print(f"Error reading database {db_path.name}: {e}")