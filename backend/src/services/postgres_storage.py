"""PostgreSQL-based storage for document metadata."""

import json

import structlog
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.schemas.api import DocumentInfo

logger = structlog.get_logger()

Base = declarative_base()


class DocumentModel(Base):
    """SQLAlchemy model for documents table."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)
    metadata = Column(Text, nullable=False)  # JSON stored as text


class PostgreSQLDocumentStorage:
    """PostgreSQL-based storage for document metadata."""

    def __init__(self, database_url: str | None = None) -> None:
        """
        Initialize PostgreSQL document storage.

        Args:
            database_url: PostgreSQL connection URL (default: from settings)
        """
        self.database_url = database_url or settings.database_url

        # Create engine and session factory
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

        logger.info("postgresql_storage_initialized", database_url=self.database_url)

    def _get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def save(self, doc_info: DocumentInfo) -> None:
        """
        Save document metadata.

        Args:
            doc_info: Document information to save
        """
        session = self._get_session()
        try:
            doc_model = DocumentModel(
                id=doc_info.id,
                filename=doc_info.filename,
                content_type=doc_info.content_type,
                uploaded_at=doc_info.uploaded_at,
                chunk_count=doc_info.chunk_count,
                metadata=json.dumps(doc_info.metadata),
            )
            session.merge(doc_model)  # Use merge for upsert
            session.commit()
            logger.debug("document_saved_postgres", doc_id=doc_info.id)
        except Exception as e:
            session.rollback()
            logger.error("postgres_save_failed", error=str(e), doc_id=doc_info.id)
            raise
        finally:
            session.close()

    def get(self, doc_id: str) -> DocumentInfo | None:
        """
        Get document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document information or None if not found
        """
        session = self._get_session()
        try:
            doc_model = session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if doc_model is None:
                return None

            return DocumentInfo(
                id=doc_model.id,
                filename=doc_model.filename,
                content_type=doc_model.content_type,
                uploaded_at=doc_model.uploaded_at,
                chunk_count=doc_model.chunk_count,
                metadata=json.loads(doc_model.metadata),
            )
        finally:
            session.close()

    def list_all(self) -> list[DocumentInfo]:
        """
        List all documents.

        Returns:
            List of all document information
        """
        session = self._get_session()
        try:
            doc_models = session.query(DocumentModel).order_by(DocumentModel.uploaded_at.desc()).all()

            documents = []
            for doc_model in doc_models:
                documents.append(
                    DocumentInfo(
                        id=doc_model.id,
                        filename=doc_model.filename,
                        content_type=doc_model.content_type,
                        uploaded_at=doc_model.uploaded_at,
                        chunk_count=doc_model.chunk_count,
                        metadata=json.loads(doc_model.metadata),
                    )
                )

            return documents
        finally:
            session.close()

    def delete(self, doc_id: str) -> bool:
        """
        Delete document metadata.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        session = self._get_session()
        try:
            doc_model = session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if doc_model is None:
                return False

            session.delete(doc_model)
            session.commit()
            logger.debug("document_deleted_from_postgres", doc_id=doc_id)
            return True
        except Exception as e:
            session.rollback()
            logger.error("postgres_delete_failed", error=str(e), doc_id=doc_id)
            return False
        finally:
            session.close()

    def exists(self, doc_id: str) -> bool:
        """
        Check if document exists.

        Args:
            doc_id: Document identifier

        Returns:
            True if document exists
        """
        return self.get(doc_id) is not None
