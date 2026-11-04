# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import sqlite3
import re
from tqdm import tqdm
from pathlib import Path


from src.lib import DocSrc, Tc, StopWord
from src.utils import PathFinder, log_execution_time
from src.operators import OpType, OpErrType, operator_error_handler


class BM25Operator:
    def __init__(self, path_finder: PathFinder, docsrc_store: dict[str, DocSrc]) -> None:
        self.path_finder = path_finder
        self.docsrc_store: dict[str, DocSrc] = docsrc_store
        self._conn: sqlite3.Connection | None = None
        self.connect()

    @operator_error_handler(OpType.BM25, OpErrType.IND)
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
                batch_ids = doc_ids[i: i + batch_size]
                placeholders = ",".join(["?"] * len(batch_ids))
                self._conn.execute(
                f"DELETE FROM fts_chunks WHERE doc_id IN ({placeholders})",  # noqa: E122
                    batch_ids
                )
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
                    batch_data = data_to_insert[i:i + batch_size]
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

    @operator_error_handler(OpType.BM25, OpErrType.SRCH)
    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        """Scores query using SQLite FTS5 built-in BM25 ranking."""

        assert isinstance(self._conn, sqlite3.Connection)
        s_cursor = self._conn.cursor()
        normalized_query = query.lower().replace("_", " ").replace("-", " ").replace(".", " ")
        s_words = re.findall(r"\w+", normalized_query)
        if not s_words:
            return []

        s_filtered_words = [w for w in s_words if w not in StopWord.STOP_WORDS]
        query_words = s_filtered_words if s_filtered_words else s_words
        safe_query = " OR ".join([f"{s_word}*" for s_word in query_words])

        query_sql = """
                    SELECT doc_id, -bm25(fts_chunks, 0.0, 0.0, 10.0, 5.0) AS score
                    FROM fts_chunks
                    WHERE fts_chunks MATCH ?
                    ORDER BY score DESC LIMIT ? \
                    """
        try:
            s_cursor.execute(query_sql, (safe_query, k))
            results = [(s_row[0], float(s_row[1])) for s_row in s_cursor.fetchall()]

            if not results and s_filtered_words != s_words:
                fallback_query = " OR ".join([f"{s_word}*" for s_word in s_words])
                s_cursor.execute(query_sql, (fallback_query, k))
                results = [(s_row[0], float(s_row[1])) for s_row in s_cursor.fetchall()]

            return results
        except sqlite3.OperationalError:
            print("ERROR RESULT EMPTY")
            return []

    @operator_error_handler(OpType.BM25, OpErrType.DEL)
    def delete(self, file_paths: Path | list[Path] | list[str] | set[Path]) -> None:
        """Surgically deletes chunks associated with file_path(s) in O(delta) time."""
        if isinstance(file_paths, Path):
            paths_to_remove = {str(file_paths)}
        else:
            paths_to_remove = {str(p) for p in file_paths}

        if not paths_to_remove:
            return

        remaining_docs = {
            doc_id: doc for doc_id, doc in self.docsrc_store.items()
            if str(doc.file_path) not in paths_to_remove
        }
        self.docsrc_store.clear()
        self.docsrc_store.update(remaining_docs)

        placeholders = ",".join(["?"] * len(paths_to_remove))
        assert isinstance(self._conn, sqlite3.Connection)
        with self._conn:
            self._conn.execute(f"DELETE FROM fts_chunks WHERE file_path IN ({placeholders})", list(paths_to_remove))
