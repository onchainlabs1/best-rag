"""RAG retriever with hybrid search and re-ranking."""

from typing import List
import chromadb
import structlog
from chromadb.config import Settings as ChromaSettings
from src.schemas.rag import DocumentChunk, RetrievalResult
from src.config import settings
from src.rag.embeddings import EmbeddingService

logger = structlog.get_logger()


class RAGRetriever:
    """Retriever for semantic search with vector database."""

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        """
        Initialize RAG retriever.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_service: Embedding service instance
        """
        self.collection_name = collection_name
        self.embedding_service = embedding_service or EmbeddingService()

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to the vector database.

        Args:
            chunks: List of document chunks to add
        """
        if not chunks:
            return

        # Generate embeddings for chunks that don't have them
        texts_to_embed: List[str] = []
        indices_to_embed: List[int] = []

        for idx, chunk in enumerate(chunks):
            if chunk.embedding is None:
                texts_to_embed.append(chunk.content)
                indices_to_embed.append(idx)

        if texts_to_embed:
            total = len(texts_to_embed)
            logger.info("generating_embeddings", total_chunks=total, provider=self.embedding_service.provider)
            
            # Use generate_embeddings to respect embedding_provider setting
            from src.schemas.rag import EmbeddingRequest
            
            embedding_request = EmbeddingRequest(texts=texts_to_embed)
            embedding_response = self.embedding_service.generate_embeddings(embedding_request)
            embeddings = embedding_response.embeddings
            
            logger.info("embeddings_generated", count=len(embeddings), provider=self.embedding_service.provider)
            
            for embed_idx, chunk_idx in enumerate(indices_to_embed):
                chunks[chunk_idx].embedding = embeddings[embed_idx]

        # Prepare data for ChromaDB and add in batches to avoid size limits
        # ChromaDB has a max batch size limit, so we process in smaller chunks
        CHROMA_BATCH_SIZE = 100  # Safe batch size for ChromaDB
        
        for batch_start in range(0, len(chunks), CHROMA_BATCH_SIZE):
            batch_end = min(batch_start + CHROMA_BATCH_SIZE, len(chunks))
            batch_chunks = chunks[batch_start:batch_end]
            
            ids: List[str] = []
            embeddings_list: List[List[float]] = []
            documents: List[str] = []
            metadatas: List[dict] = []

            for chunk in batch_chunks:
                if chunk.embedding is None:
                    continue

                chunk_id = chunk.chunk_id or f"{chunk.source}_{chunk.position}"
                ids.append(chunk_id)
                embeddings_list.append(chunk.embedding)
                documents.append(chunk.content)
                metadatas.append(chunk.metadata)

            if ids:
                logger.info("adding_chunks_to_chromadb", batch_size=len(ids), total_chunks=len(chunks))
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings_list,
                    documents=documents,
                    metadatas=metadatas,
                )
        
        logger.info("all_chunks_added_to_chromadb", total_chunks=len(chunks))

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filter_metadata: dict | None = None,
    ) -> RetrievalResult:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filter_metadata: Optional metadata filters

        Returns:
            Retrieval result with chunks and scores
        """
        # Log collection info for debugging
        try:
            collection_count = self.collection.count()
            logger.info("retrieving_from_collection", collection_name=self.collection_name, total_docs=collection_count, query=query)
        except Exception as e:
            logger.warning("failed_to_count_collection", error=str(e))

        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        logger.debug("query_embedding_generated", embedding_dim=len(query_embedding))

        # Query ChromaDB
        where = filter_metadata if filter_metadata else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )
        
        # Log detailed query results for debugging
        result_ids_count = 0
        if results.get("ids") and len(results["ids"]) > 0 and results["ids"][0]:
            result_ids_count = len(results["ids"][0])
        
        logger.info("chromadb_query_results", 
                   found_ids=result_ids_count,
                   requested_top_k=top_k,
                   has_ids=bool(results.get("ids")),
                   has_documents=bool(results.get("documents")),
                   has_distances=bool(results.get("distances")))

        # Process results
        chunks: List[DocumentChunk] = []
        scores: List[float] = []

        # More robust check for results
        if results.get("ids") and len(results["ids"]) > 0 and results["ids"][0] and len(results["ids"][0]) > 0:
            for idx, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns cosine distance (0 = identical, 1 = orthogonal)
                # Convert to similarity score (higher = more similar)
                if results["distances"] and len(results["distances"][0]) > idx:
                    distance = results["distances"][0][idx]
                else:
                    distance = 0.5  # Default distance if not available
                similarity = 1.0 - distance  # Cosine distance to similarity

                # Log similarity scores for debugging
                logger.info("retrieval_score", doc_id=str(doc_id), similarity=similarity, threshold=score_threshold, idx=idx)

                # Sempre incluir resultados se threshold for 0.0
                # Se threshold > 0, incluir se similarity >= threshold OU se for o primeiro resultado (para garantir pelo menos algo)
                should_include = False
                if score_threshold <= 0.0:
                    should_include = True
                elif similarity >= score_threshold:
                    should_include = True
                elif idx == 0:
                    # Incluir o primeiro resultado mesmo com score baixo para garantir que temos algo
                    logger.info("including_first_result_despite_low_score", similarity=similarity, threshold=score_threshold)
                    should_include = True
                
                if not should_include:
                    logger.debug("skipping_result_below_threshold", similarity=similarity, threshold=score_threshold)
                    continue

                # Safely extract content and metadata
                content = ""
                if results.get("documents") and len(results["documents"]) > 0:
                    if len(results["documents"][0]) > idx:
                        content = results["documents"][0][idx] or ""
                
                metadata = {}
                if results.get("metadatas") and len(results["metadatas"]) > 0:
                    if len(results["metadatas"][0]) > idx:
                        metadata = results["metadatas"][0][idx] or {}

                # Find embedding if available (ChromaDB may not return embeddings by default)
                embedding = None
                if results.get("embeddings") and len(results["embeddings"]) > 0:
                    if len(results["embeddings"][0]) > idx:
                        embedding = results["embeddings"][0][idx]

                chunk = DocumentChunk(
                    content=content,
                    metadata=metadata,
                    chunk_id=str(doc_id),
                    source=metadata.get("source"),
                    position=metadata.get("position"),
                    embedding=embedding,
                )
                chunks.append(chunk)
                scores.append(similarity)

        logger.info("retrieval_final_result", 
                   chunks_returned=len(chunks),
                   scores_count=len(scores),
                   first_score=scores[0] if scores else None)
        
        return RetrievalResult(
            chunks=chunks,
            scores=scores,
            query=query,
            total_results=len(chunks),
        )

    def delete_collection(self) -> None:
        """Delete the collection (useful for testing)."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass  # Collection might not exist
