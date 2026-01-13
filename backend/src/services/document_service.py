"""Document service for managing documents."""

from typing import List
import uuid
from datetime import datetime
from src.rag.chunking import DocumentChunker
from src.rag.retriever import RAGRetriever
from src.schemas.api import DocumentInfo, DocumentUpload
from src.services.document_parser import DocumentParser
from src.config import settings
import structlog

logger = structlog.get_logger()


class DocumentService:
    """Service for managing documents in the knowledge base."""

    def __init__(
        self,
        chunker: DocumentChunker | None = None,
        retriever: RAGRetriever | None = None,
        parser: DocumentParser | None = None,
    ) -> None:
        """
        Initialize document service.

        Args:
            chunker: Document chunker instance
            retriever: RAG retriever instance
            parser: Document parser instance (for PDF extraction)
        """
        self.chunker = chunker or DocumentChunker()
        self.retriever = retriever or RAGRetriever()
        self.parser = parser or DocumentParser()
        self.documents: dict[str, DocumentInfo] = {}

    def upload_document(self, upload: DocumentUpload) -> DocumentInfo:
        """
        Upload and process a document.

        Args:
            upload: Document upload request

        Returns:
            Document information
        """
        doc_id = str(uuid.uuid4())
        content_size = len(upload.content)
        logger.info("uploading_document", doc_id=doc_id, filename=upload.filename, size=content_size)

        # Parse document content (especially important for PDFs)
        logger.info("parsing_document", doc_id=doc_id, filename=upload.filename, content_type=upload.content_type)
        parsed_content = self.parser.parse_document(
            content=upload.content,
            filename=upload.filename,
            content_type=upload.content_type,
        )
        
        if not parsed_content or len(parsed_content.strip()) == 0:
            logger.warning("no_content_extracted", doc_id=doc_id, filename=upload.filename)
            # If no content extracted, use original content as fallback
            parsed_content = upload.content
        
        logger.info("document_parsed", doc_id=doc_id, extracted_length=len(parsed_content))

        # Chunk document
        logger.info("chunking_document", doc_id=doc_id)
        chunks = self.chunker.chunk_document(
            content=parsed_content,
            source=doc_id,
            metadata=upload.metadata,
        )
        logger.info("document_chunked", doc_id=doc_id, chunks_count=len(chunks))

        # Add chunks to retriever
        logger.info("indexing_chunks", doc_id=doc_id, chunks_count=len(chunks))
        self.retriever.add_documents(chunks)
        logger.info("chunks_indexed", doc_id=doc_id)

        # Create document info
        doc_info = DocumentInfo(
            id=doc_id,
            filename=upload.filename,
            content_type=upload.content_type,
            uploaded_at=datetime.now(),
            chunk_count=len(chunks),
            metadata=upload.metadata,
        )

        # Store document info
        self.documents[doc_id] = doc_info

        logger.info("document_uploaded", doc_id=doc_id, chunks=len(chunks))

        return doc_info

    def list_documents(self) -> List[DocumentInfo]:
        """
        List all documents.

        Returns:
            List of document information
        """
        return list(self.documents.values())

    def get_document(self, doc_id: str) -> DocumentInfo | None:
        """
        Get document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document information or None if not found
        """
        return self.documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its chunks from the vector database.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        if doc_id not in self.documents:
            return False
        
        # Delete chunks from ChromaDB
        # Chunk IDs follow pattern: {doc_id}_chunk_{index} or {doc_id}_{position}
        try:
            # Get all chunks for this document from ChromaDB
            # ChromaDB doesn't have a direct "get by metadata" query, so we need to:
            # 1. Query with metadata filter (if supported)
            # 2. Or get all and filter (less efficient but works)
            
            # Try to get chunks by querying with metadata filter
            try:
                results = self.retriever.collection.get(
                    where={"source": doc_id},
                    include=["metadatas", "ids"]
                )
                
                if results and results.get("ids"):
                    chunk_ids = results["ids"]
                    if chunk_ids:
                        logger.info("deleting_chunks_from_chromadb", doc_id=doc_id, chunk_count=len(chunk_ids))
                        self.retriever.collection.delete(ids=chunk_ids)
                        logger.info("chunks_deleted_from_chromadb", doc_id=doc_id, deleted_count=len(chunk_ids))
            except Exception as e:
                # Fallback: try to delete by pattern matching IDs
                logger.warning("metadata_filter_not_supported", error=str(e))
                try:
                    # Get all IDs and filter by prefix
                    all_results = self.retriever.collection.get(include=["metadatas", "ids"])
                    if all_results and all_results.get("ids"):
                        chunk_ids_to_delete = [
                            chunk_id for chunk_id, metadata in zip(
                                all_results["ids"],
                                all_results.get("metadatas", [])
                            )
                            if isinstance(metadata, dict) and metadata.get("source") == doc_id
                        ]
                        if chunk_ids_to_delete:
                            self.retriever.collection.delete(ids=chunk_ids_to_delete)
                            logger.info("chunks_deleted_by_pattern", doc_id=doc_id, deleted_count=len(chunk_ids_to_delete))
                except Exception as e2:
                    logger.error("failed_to_delete_chunks", doc_id=doc_id, error=str(e2))
        
        except Exception as e:
            logger.error("error_deleting_chunks", doc_id=doc_id, error=str(e))
            # Continue to delete from memory even if ChromaDB delete fails
        
        # Delete from memory
        del self.documents[doc_id]
        logger.info("document_deleted", doc_id=doc_id)
        return True
