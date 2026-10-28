# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import sqlite3
import re
import json
from tqdm import tqdm
from pathlib import Path

from src.lib import DocSrc, Tc, Sw
from src.utils import PathFinder
from src.utils.decorators import log_execution_time


class BM25Operator:
    def __init__(self, path_finder: PathFinder, docsrc_store: dict[str, DocSrc]) -> None:
        self.path_finder = path_finder
        self.docsrc_store: dict[str, DocSrc] = docsrc_store
        self._conn: sqlite3.Connection | None = None
        self.connect()

    @log_execution_time
    def index(self, target_docs: dict[str, DocSrc] | None = None) -> None:
        """True incremental indexing: upserts only the target_docs in O(delta) time."""

        if target_docs is not None and len(target_docs) == 0:
            return

        docs_to_index = self.docsrc_store if target_docs is None else target_docs
        if not docs_to_index:
            return
        doc_ids = list(docs_to_index.keys())
        batch_size = 500
        total_docs = len(doc_ids)

        assert isinstance(self._conn, sqlite3.Connection)
        with self._conn:
            for i in range(0, total_docs, batch_size):
                batch_ids = doc_ids[i : i + batch_size]
                placeholders = ",".join(["?"] * len(batch_ids))
                self._conn.execute(
                f"DELETE FROM fts_chunks WHERE doc_id IN ({placeholders})",
                    batch_ids)
            data_to_insert = [
                (doc_id, str(doc.file_path), doc.hierarchy, doc.text)
                for doc_id, doc in docs_to_index.items()
            ]
            with tqdm(
                    total=total_docs,
                    desc=f"{Tc.org}[SQLite FTS5]{Tc.clr} Lexical Indexing",
                    unit="doc",
                    colour="yellow") as pbar:
                for i in range(0, total_docs, batch_size):
                    batch_data = data_to_insert[ i : i + batch_size]
                    self._conn.executemany(
                        "INSERT INTO fts_chunks (doc_id, file_path, hierarchy, content) VALUES (?, ?, ?, ?)",
                        batch_data
                    )
                    pbar.update(len(batch_data))

    def connect(self) -> None:
        if self._conn is None:
            self.path_finder.bm25_dir.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.path_finder.database_path))
            assert isinstance(self._conn, sqlite3.Connection)
            self._conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
                    doc_id UNINDEXED,
                    file_path UNINDEXED,
                    hierarchy,
                    content,
                    tokenize='unicode61 remove_diacritics 1'
                );
            """)
            self._conn.commit()

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        """Scores query using SQLite FTS5 built-in BM25 ranking."""

        assert isinstance(self._conn, sqlite3.Connection)
        cursor = self._conn.cursor()
        normalized_query = query.lower().replace("_", " ").replace("-", " ").replace(".", " ")
        words = re.findall(r"\w+", normalized_query)
        # words = re.findall(r"\w+", query.lower())
        if not words:
            return []

        filtered_words = [w for w in words if w not in Sw.STOP_WORDS]
        query_words = filtered_words if filtered_words else words
        safe_query = " OR ".join([f"{word}*" for word in query_words])

        query_sql = """
                    SELECT doc_id, -bm25(fts_chunks, 0.0, 0.0, 10.0, 5.0) AS score
                    FROM fts_chunks
                    WHERE fts_chunks MATCH ?
                    ORDER BY score DESC LIMIT ? \
                    """
        try:
            cursor.execute(query_sql, (safe_query, k))
            results = [(row[0], float(row[1])) for row in cursor.fetchall()]

            if not results and filtered_words != words:
                fallback_query = " OR ".join([f"{word}*" for word in words])
                cursor.execute(query_sql, (fallback_query, k))
                results = [(row[0], float(row[1])) for row in cursor.fetchall()]

            return results
        except sqlite3.OperationalError:
            print("ERROR RESULT EMPTY")
            return []

    def delete(self, file_paths: Path | list[Path] | set[Path]) -> None:
        """Surgically deletes chunks associated with file_path(s) in O(delta) time."""
        if isinstance(file_paths, Path):
            paths_to_remove = {str(file_paths)}
        else:
            paths_to_remove = {str(p) for p in file_paths}

        if not paths_to_remove:
            return

        # 1. Prune from memory store
        remaining_docs = {
            doc_id: doc for doc_id, doc in self.docsrc_store.items()
            if str(doc.file_path) not in paths_to_remove
        }
        self.docsrc_store.clear()
        self.docsrc_store.update(remaining_docs)

        # 2. Surgically delete from SQLite FTS5 table instantly
        placeholders = ",".join(["?"] * len(paths_to_remove))
        assert isinstance(self._conn, sqlite3.Connection)
        with self._conn:
            self._conn.execute(f"DELETE FROM fts_chunks WHERE file_path IN ({placeholders})", list(paths_to_remove))

        def debug_inspect_tokens(self, prefix: str = "") -> None:
            """Inspects tokens stored in the FTS5 index to verify tokenization behavior."""
            assert isinstance(self._conn, sqlite3.Connection)
            cursor = self._conn.cursor()

            # Create an auxiliary vocab table mapping to your fts_chunks table
            cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_vocab USING fts5vocab('fts_chunks', 'row');")

            query = "SELECT term, doc/cnt FROM fts_vocab"
            params = ()
            if prefix:
                query += " WHERE term LIKE ?"
                params = (f"{prefix}%",)

            cursor.execute(query, params)
            print(f"{'TERM':<30} | {'DOCUMENT FREQUENCY'}")
            print("-" * 50)
            for row in cursor.fetchall():
                print(f"{row[0]:<30} | {row[1]}")

            # Clean up vocab table
            cursor.execute("DROP TABLE IF EXISTS fts_vocab;")


if __name__ == "__main__":
    path_finder = PathFinder()
    with open(path_finder.docsrc_path, "r", encoding="utf-8") as f:
        raw_docs: list[dict] = json.load(f)

    docsrc_store = {
        item["id"]: DocSrc.model_validate(item)
        for item in raw_docs
    }
    bm25_op = BM25Operator(path_finder, docsrc_store)

    assert isinstance(bm25_op._conn, sqlite3.Connection)
    cursor = bm25_op._conn.cursor()

    # Drop an actual question string from one of your "No index overlap" failures here
    failing_query = "What is the CLI command for starting a chat interface in vLLM?"
    words = re.findall(r"\w+", failing_query.lower())
    filtered_words = [w for w in words if w not in Sw.STOP_WORDS]

    print(f"\nAuditing tokens for query: '{failing_query}'\n")
    cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_vocab USING fts5vocab('fts_chunks', 'row');")

    for word in filtered_words:
        cursor.execute("SELECT term, cnt FROM fts_vocab WHERE term = ?", (word,))
        row = cursor.fetchone()
        if row:
            print(f"  [FOUND]    '{row[0]}' (appears in {row[1]} chunks)")
        else:
            print(f"  [MISSING]  '{word}' -> ZERO match in index! (This is why it failed)")

    cursor.execute("DROP TABLE IF EXISTS fts_vocab;")
