import hashlib
import os
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


class KnowledgeStore:
    """Small SQLite-backed store for document metadata and searchable chunks."""

    def __init__(self, db_path: str | Path | None = None):
        configured_path = db_path or os.getenv("EKP_DB_PATH", "data/knowledge.db")
        self.db_path = Path(configured_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with closing(self._connect()) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        sha256 TEXT NOT NULL,
                        uploaded_at TEXT NOT NULL,
                        content_type TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_chunks_document
                        ON chunks(document_id, chunk_index);
                    """
                )

    def add_document(self, filename: str, content_type: str, raw_content: bytes, chunks: list[str]):
        document_id = str(uuid.uuid4())
        uploaded_at = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(raw_content).hexdigest()
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """INSERT INTO documents (id, filename, sha256, uploaded_at, content_type)
                       VALUES (?, ?, ?, ?, ?)""",
                    (document_id, filename, digest, uploaded_at, content_type),
                )
                connection.executemany(
                    "INSERT INTO chunks (document_id, chunk_index, content) VALUES (?, ?, ?)",
                    [(document_id, index, chunk) for index, chunk in enumerate(chunks)],
                )
        return {
            "document_id": document_id,
            "filename": filename,
            "sha256": digest,
            "uploaded_at": uploaded_at,
            "chunk_count": len(chunks),
        }

    def get_document(self, document_id: str):
        with closing(self._connect()) as connection:
            row = connection.execute(
                """SELECT d.id, d.filename, d.sha256, d.uploaded_at, d.content_type,
                          COUNT(c.id) AS chunk_count
                   FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
                   WHERE d.id = ? GROUP BY d.id""",
                (document_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def search(self, query: str, limit: int = 10):
        terms = list(dict.fromkeys(re.findall(r"[a-zA-Z0-9_]{2,}", query.lower())))
        if not terms:
            return []
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """SELECT c.document_id, c.chunk_index, c.content, d.filename
                   FROM chunks c JOIN documents d ON d.id = c.document_id"""
            ).fetchall()

        results = []
        for row in rows:
            lowered = row["content"].lower()
            score = sum(lowered.count(term) for term in terms)
            if score:
                results.append({
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "chunk_index": row["chunk_index"],
                    "excerpt": row["content"],
                    "score": score,
                })
        results.sort(key=lambda item: (-item["score"], item["filename"], item["chunk_index"]))
        return results[: max(1, min(limit, 50))]
