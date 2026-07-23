from __future__ import annotations

import sqlite3
from pathlib import Path

from control_tower.domain.models import AtomicChunk, SearchHit


class SQLiteStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS dependencies (
                    parent_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    UNIQUE(parent_id, child_id)
                );
                CREATE TABLE IF NOT EXISTS node_state (
                    node_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'fresh'
                );
                """
            )

    def save_chunks(self, chunks: list[AtomicChunk]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO chunks(id, document_id, ordinal, text, content_hash, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.id,
                        c.document_id,
                        c.ordinal,
                        c.text,
                        c.content_hash,
                        c.model_dump_json(),
                    )
                    for c in chunks
                ],
            )
            conn.executemany(
                "INSERT OR REPLACE INTO node_state(node_id, version, status) VALUES (?, 1, 'fresh')",
                [(c.id,) for c in chunks],
            )

    def replace_document_chunks(self, document_id: str, chunks: list[AtomicChunk]) -> None:
        """Remplace atomiquement tous les chunks d'un document après enrichissement."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id FROM chunks WHERE document_id=?", (document_id,)
            ).fetchall()
            old_ids = [row["id"] for row in rows]
            if old_ids:
                placeholders = ",".join("?" for _ in old_ids)
                conn.execute(
                    f"DELETE FROM dependencies WHERE parent_id IN ({placeholders}) "
                    f"OR child_id IN ({placeholders})",
                    (*old_ids, *old_ids),
                )
                conn.executemany(
                    "DELETE FROM node_state WHERE node_id=?", [(item,) for item in old_ids]
                )
            conn.execute("DELETE FROM chunks WHERE document_id=?", (document_id,))
            conn.executemany(
                """
                INSERT INTO chunks(id, document_id, ordinal, text, content_hash, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.id,
                        c.document_id,
                        c.ordinal,
                        c.text,
                        c.content_hash,
                        c.model_dump_json(),
                    )
                    for c in chunks
                ],
            )
            conn.executemany(
                "INSERT INTO node_state(node_id, version, status) VALUES (?, 1, 'fresh')",
                [(c.id,) for c in chunks],
            )

    def all_chunks(self) -> list[AtomicChunk]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM chunks ORDER BY document_id, ordinal").fetchall()
        return [AtomicChunk.model_validate_json(row["payload"]) for row in rows]

    def chunks_for_document(self, document_id: str) -> list[AtomicChunk]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload FROM chunks WHERE document_id=? ORDER BY ordinal",
                (document_id,),
            ).fetchall()
        return [AtomicChunk.model_validate_json(row["payload"]) for row in rows]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        import re
        import unicodedata

        normalized = unicodedata.normalize("NFKC", text).casefold()
        return {
            token
            for token in re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", normalized, flags=re.UNICODE)
            if len(token) > 2
        }

    def search(
        self, query: str, top_k: int = 5, *, canonical_only: bool = True
    ) -> list[SearchHit]:
        terms = self._tokens(query)
        if not terms:
            return []
        scored: list[SearchHit] = []
        for chunk in self.all_chunks():
            if canonical_only and not chunk.indexable:
                continue
            words = self._tokens(chunk.text)
            overlap = len(terms & words)
            if overlap:
                score = overlap / len(terms)
                scored.append(SearchHit(chunk=chunk, score=score))
        return sorted(scored, key=lambda hit: hit.score, reverse=True)[:top_k]

    def add_dependency(self, parent_id: str, child_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO dependencies(parent_id, child_id) VALUES (?, ?)",
                (parent_id, child_id),
            )

    def descendants(self, node_id: str) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                WITH RECURSIVE descendants(id) AS (
                    SELECT child_id FROM dependencies WHERE parent_id = ?
                    UNION
                    SELECT d.child_id FROM dependencies d JOIN descendants x ON d.parent_id = x.id
                )
                SELECT id FROM descendants
                """,
                (node_id,),
            ).fetchall()
        return [row["id"] for row in rows]

    def mark_stale(self, node_ids: list[str]) -> None:
        if not node_ids:
            return
        with self._connect() as conn:
            conn.executemany(
                "UPDATE node_state SET status='stale', version=version+1 WHERE node_id=?",
                [(node_id,) for node_id in node_ids],
            )

    def state(self, node_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT node_id, version, status FROM node_state WHERE node_id=?", (node_id,)
            ).fetchone()
        return dict(row) if row else None

    def stats(self) -> dict:
        with self._connect() as conn:
            chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            document_count = conn.execute(
                "SELECT COUNT(DISTINCT document_id) FROM chunks"
            ).fetchone()[0]
            stale_count = conn.execute(
                "SELECT COUNT(*) FROM node_state WHERE status='stale'"
            ).fetchone()[0]
            dependency_count = conn.execute("SELECT COUNT(*) FROM dependencies").fetchone()[0]
            canonical_count = conn.execute(
                "SELECT COUNT(*) FROM chunks WHERE json_extract(payload, '$.indexable') = 1"
            ).fetchone()[0]
        return {
            "chunks": chunk_count,
            "canonical_chunks": canonical_count,
            "duplicate_chunks": chunk_count - canonical_count,
            "documents": document_count,
            "stale_nodes": stale_count,
            "dependencies": dependency_count,
        }
