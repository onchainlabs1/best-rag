"""Document endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List
from src.schemas.api import (
    DocumentUpload, 
    DocumentList, 
    DocumentInfo,
    BatchDocumentUpload,
    BatchDocumentUploadResponse,
)
from src.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

# Service instance - use shared instance
from src.shared_services import document_service


@router.post("", response_model=DocumentInfo, status_code=status.HTTP_201_CREATED)
async def upload_document(upload: DocumentUpload) -> DocumentInfo:
    """
    Upload a document to the knowledge base.

    Args:
        upload: Document upload request

    Returns:
        Document information
    """
    import asyncio
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        # Process in background to avoid blocking
        # For now, process synchronously but log progress
        logger.info("document_upload_started", filename=upload.filename, size=len(upload.content))
        
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        doc = await loop.run_in_executor(
            None,
            document_service.upload_document,
            upload
        )
        
        logger.info("document_upload_completed", doc_id=doc.id, chunks=doc.chunk_count)
        return doc
    except Exception as e:
        logger.error("document_upload_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        ) from e


@router.get("", response_model=DocumentList)
async def list_documents() -> DocumentList:
    """
    List all documents in the knowledge base.

    Returns:
        List of documents
    """
    documents = document_service.list_documents()
    return DocumentList(documents=documents, total=len(documents))


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: str) -> DocumentInfo:
    """
    Get a document by ID.

    Args:
        doc_id: Document identifier

    Returns:
        Document information
    """
    doc = document_service.get_document(doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
    return doc


@router.post("/batch", response_model=BatchDocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents_batch(batch: BatchDocumentUpload) -> BatchDocumentUploadResponse:
    """
    Upload multiple documents in batch.

    Args:
        batch: Batch document upload request

    Returns:
        Batch upload response with results
    """
    import asyncio
    import structlog
    
    logger = structlog.get_logger()
    
    uploaded_docs: List[DocumentInfo] = []
    errors: List[dict] = []
    
    logger.info("batch_upload_started", count=len(batch.documents))
    
    # Process documents sequentially to avoid overwhelming the system
    loop = asyncio.get_event_loop()
    
    for idx, upload in enumerate(batch.documents):
        try:
            logger.info("batch_upload_item", index=idx, filename=upload.filename)
            doc = await loop.run_in_executor(
                None,
                document_service.upload_document,
                upload
            )
            uploaded_docs.append(doc)
            logger.info("batch_upload_item_success", index=idx, doc_id=doc.id)
        except Exception as e:
            error_info = {
                "filename": upload.filename,
                "error": str(e),
                "index": idx,
            }
            errors.append(error_info)
            logger.error("batch_upload_item_failed", index=idx, filename=upload.filename, error=str(e))
    
    logger.info(
        "batch_upload_completed",
        total=len(batch.documents),
        success=len(uploaded_docs),
        errors=len(errors)
    )
    
    return BatchDocumentUploadResponse(
        documents=uploaded_docs,
        errors=errors,
        total=len(batch.documents),
        success_count=len(uploaded_docs),
        error_count=len(errors),
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str) -> None:
    """
    Delete a document.

    Args:
        doc_id: Document identifier
    """
    deleted = document_service.delete_document(doc_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
