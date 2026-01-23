"""Document metadata storage using SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import structlog

from src.config import settings
from src.schemas.api import DocumentInfo

logger = structlog.get_logger()


class DocumentStorage:
    """SQLite-based storage for document metadata."""

    def __init__(self, db_path: str | None = None) -> None:
        """
        Initialize document storage.

        Args:
            db_path: Path to SQLite database file (default: ./data/documents.db)
        """
        if db_path is None:
            # Use data directory from chroma_path setting
            data_dir = Path(settings.chroma_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "documents.db")

        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                metadata TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        logger.info("document_storage_initialized", db_path=self.db_path)

    def save(self, doc_info: DocumentInfo) -> None:
        """
        Save document metadata.

        Args:
            doc_info: Document information to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO documents
            (id, filename, content_type, uploaded_at, chunk_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                doc_info.id,
                doc_info.filename,
                doc_info.content_type,
                doc_info.uploaded_at.isoformat(),
                doc_info.chunk_count,
                json.dumps(doc_info.metadata),
            ),
        )

        conn.commit()
        conn.close()
        logger.debug("document_saved", doc_id=doc_info.id)

    def get(self, doc_id: str) -> DocumentInfo | None:
        """
        Get document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document information or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, filename, content_type, uploaded_at, chunk_count, metadata
            FROM documents
            WHERE id = ?
        """,
            (doc_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return DocumentInfo(
            id=row[0],
            filename=row[1],
            content_type=row[2],
            uploaded_at=datetime.fromisoformat(row[3]),
            chunk_count=row[4],
            metadata=json.loads(row[5]),
        )

    def list_all(self) -> list[DocumentInfo]:
        """
        List all documents.

        Returns:
            List of all document information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, filename, content_type, uploaded_at, chunk_count, metadata
            FROM documents
            ORDER BY uploaded_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        documents = []
        for row in rows:
            documents.append(
                DocumentInfo(
                    id=row[0],
                    filename=row[1],
                    content_type=row[2],
                    uploaded_at=datetime.fromisoformat(row[3]),
                    chunk_count=row[4],
                    metadata=json.loads(row[5]),
                )
            )

        return documents

    def delete(self, doc_id: str) -> bool:
        """
        Delete document metadata.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        if deleted:
            logger.debug("document_deleted_from_storage", doc_id=doc_id)

        return deleted

    def exists(self, doc_id: str) -> bool:
        """
        Check if document exists.

        Args:
            doc_id: Document identifier

        Returns:
            True if document exists
        """
        return self.get(doc_id) is not None
