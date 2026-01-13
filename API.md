# API Documentation

Complete API reference for the RAG + Agent Knowledge Base System.

## Base URL

- **Local**: `http://localhost:8080`
- **API Version**: `v1`
- **Base Path**: `/api/v1`

## Authentication

Currently, no authentication is required. In production, implement API key or OAuth.

## Endpoints

### Health Check

#### `GET /api/v1/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-01-12T10:51:30.130758"
}
```

### Documents

#### `POST /api/v1/documents`

Upload a document to the knowledge base.

**Request:**
```json
{
  "filename": "document.pdf",
  "content": "base64_encoded_content_or_plain_text",
  "content_type": "application/pdf",
  "metadata": {}
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "uploaded_at": "2025-01-12T10:00:00",
  "chunk_count": 42,
  "metadata": {}
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8080/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "example.pdf",
    "content": "base64_content_here",
    "content_type": "application/pdf",
    "metadata": {}
  }'
```

#### `GET /api/v1/documents`

List all uploaded documents.

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid-1",
      "filename": "doc1.pdf",
      "uploaded_at": "2025-01-12T10:00:00",
      "chunk_count": 42
    }
  ],
  "total": 1
}
```

#### `DELETE /api/v1/documents/{doc_id}`

Delete a document and its chunks.

**Response:** `204 No Content`

### Queries

#### `POST /api/v1/queries`

Process a query and get an answer (non-streaming).

**Request:**
```json
{
  "query": "What is RAG?",
  "top_k": 5,
  "score_threshold": 0.3,
  "stream": false
}
```

**Response:**
```json
{
  "answer": "RAG (Retrieval-Augmented Generation) is...",
  "sources": [
    {
      "chunk_id": "doc_id_chunk_0",
      "content": "Document excerpt...",
      "source": "doc_id",
      "score": 0.85,
      "metadata": {}
    }
  ],
  "score": 0.92,
  "metadata": {
    "iteration_count": 1,
    "citations_count": 3
  }
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8080/api/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "top_k": 5,
    "score_threshold": 0.3,
    "stream": false
  }'
```

### Agent Chat (Streaming)

#### `POST /api/v1/agents/chat`

Chat with the agent using Server-Sent Events (SSE) for streaming responses.

**Request:**
```json
{
  "query": "Explain how embeddings work",
  "top_k": 5,
  "score_threshold": 0.3,
  "stream": true
}
```

**Response:** Server-Sent Events stream

```
data: {"node": "retrieve", "state": {...}}
data: {"node": "generate", "state": {...}}
data: {"node": "validate", "state": {...}}
data: [DONE]
```

**Example (JavaScript):**
```javascript
const eventSource = new EventSource('http://localhost:8080/api/v1/agents/chat', {
  method: 'POST',
  body: JSON.stringify({
    query: "What is RAG?",
    top_k: 5,
    score_threshold: 0.3,
    stream: true
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

## Request/Response Schemas

### QueryRequest

```typescript
{
  query: string;           // User question
  top_k?: number;          // Number of documents to retrieve (default: 5)
  score_threshold?: number; // Minimum similarity score (default: 0.3)
  stream?: boolean;        // Enable streaming (default: false)
}
```

### QueryResponse

```typescript
{
  answer: string;          // Generated answer
  sources: SourceInfo[];   // Source documents
  score: number;           // Validation score (0.0-1.0)
  metadata: {
    iteration_count: number;
    citations_count: number;
  };
}
```

### SourceInfo

```typescript
{
  chunk_id: string;        // Unique chunk identifier
  content: string;         // Chunk content (truncated to 200 chars)
  source: string;          // Source document ID
  score: number;           // Similarity score (0.0-1.0)
  metadata: object;        // Additional metadata
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200` - Success
- `201` - Created (document upload)
- `204` - No Content (delete)
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently not implemented. In production, implement rate limiting per IP/user.

## Best Practices

1. **Use appropriate `score_threshold`**: Lower (0.2-0.3) for more results, higher (0.7-0.9) for precision
2. **Batch document uploads**: Upload multiple documents sequentially
3. **Monitor `iteration_count`**: High values may indicate poor retrieval
4. **Check `validation_score`**: Values below 0.5 may indicate low-quality answers

## Interactive API Documentation

Visit `http://localhost:8080/docs` for interactive Swagger/OpenAPI documentation.
