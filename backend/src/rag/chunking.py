"""Document chunking implementation."""

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback for older LangChain versions
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.schemas.rag import DocumentChunk


class DocumentChunker:
    """Handles intelligent document chunking with overlap and metadata preservation."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ) -> None:
        """
        Initialize document chunker.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks for context preservation
            separators: Custom separators for splitting (default: recursive splitting)
        """
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_document(
        self,
        content: str,
        source: str | None = None,
        metadata: dict | None = None,
    ) -> list[DocumentChunk]:
        """
        Split document into chunks.

        Args:
            content: Document content to chunk
            source: Source document identifier
            metadata: Additional metadata for all chunks

        Returns:
            List of document chunks with metadata
        """
        if metadata is None:
            metadata = {}

        # Split text using LangChain splitter
        text_chunks = self.splitter.split_text(content)

        # Create DocumentChunk objects
        chunks: list[DocumentChunk] = []
        for idx, text in enumerate(text_chunks):
            chunk_metadata = {
                **metadata,
                "position": idx,
                "source": source,
                "chunk_index": idx,
            }

            chunk = DocumentChunk(
                content=text,
                metadata=chunk_metadata,
                chunk_id=f"{source}_chunk_{idx}" if source else f"chunk_{idx}",
                source=source,
                position=idx,
            )
            chunks.append(chunk)

        return chunks

    def chunk_documents(
        self,
        documents: list[dict],
    ) -> list[DocumentChunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of documents with 'content' and optional 'source' and 'metadata'

        Returns:
            List of all document chunks
        """
        all_chunks: list[DocumentChunk] = []
        for doc in documents:
            content = doc.get("content", "")
            source = doc.get("source")
            metadata = doc.get("metadata", {})
            chunks = self.chunk_document(content, source, metadata)
            all_chunks.extend(chunks)

        return all_chunks
