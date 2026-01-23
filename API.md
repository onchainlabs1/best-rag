# API Documentation

Complete API reference for the RAG + Agent Knowledge Base system.

## Base URL

- **Development**: `http://localhost:8080`
- **Production**: Configure via environment variables

All endpoints are prefixed with `/api/v1`.

## Authentication

Currently, no authentication is required. For production deployments, implement API key authentication or OAuth 2.0.

## Rate Limiting

Rate limiting is enabled by default and can be configured via environment variables:

- **Queries**: 10 requests per minute (default)
- **Document Uploads**: 5 requests per minute (default)
- **Agent Chat**: 20 requests per minute (default)

When rate limit is exceeded, the API returns `429 Too Many Requests` with the following response:

```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

Rate limiting can be disabled by setting `RATE_LIMIT_ENABLED=false` in your `.env` file.

## Endpoints

### Documents

#### Upload Document

Upload a single document to the knowledge base.

**Endpoint**: `POST /api/v1/documents`

**Request Body**:
```json
{
  "filename": "example.pdf",
  "content": "base64_encoded_content_here",
  "content_type": "application/pdf",
  "metadata": {
    "author": "John Doe",
    "category": "technical"
  }
}
```

**Parameters**:
- `filename` (string, required): Name of the file (1-255 characters)
- `content` (string, required): Document content, base64 encoded (max ~50MB)
- `content_type` (string, optional): MIME type (default: "text/plain")
- `metadata` (object, optional): Additional metadata

**Response**: `201 Created`
```json
{
  "id": "doc_123",
  "filename": "example.pdf",
  "content_type": "application/pdf",
  "uploaded_at": "2026-01-23T10:00:00Z",
  "chunk_count": 15,
  "metadata": {
    "author": "John Doe",
    "category": "technical"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body or validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error during processing

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "example.txt",
    "content": "VGhpcyBpcyB0ZXN0IGNvbnRlbnQ=",
    "content_type": "text/plain"
  }'
```

#### List Documents

Get a list of all uploaded documents.

**Endpoint**: `GET /api/v1/documents`

**Response**: `200 OK`
```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "example.pdf",
      "content_type": "application/pdf",
      "uploaded_at": "2026-01-23T10:00:00Z",
      "chunk_count": 15,
      "metadata": {}
    }
  ],
  "total": 1
}
```

**Example**:
```bash
curl http://localhost:8080/api/v1/documents
```

#### Get Document

Get information about a specific document.

**Endpoint**: `GET /api/v1/documents/{doc_id}`

**Path Parameters**:
- `doc_id` (string, required): Document identifier

**Response**: `200 OK`
```json
{
  "id": "doc_123",
  "filename": "example.pdf",
  "content_type": "application/pdf",
  "uploaded_at": "2026-01-23T10:00:00Z",
  "chunk_count": 15,
  "metadata": {}
}
```

**Error Responses**:
- `404 Not Found`: Document not found

**Example**:
```bash
curl http://localhost:8080/api/v1/documents/doc_123
```

#### Delete Document

Delete a document and all its chunks from the knowledge base.

**Endpoint**: `DELETE /api/v1/documents/{doc_id}`

**Path Parameters**:
- `doc_id` (string, required): Document identifier

**Response**: `204 No Content`

**Error Responses**:
- `404 Not Found`: Document not found
- `429 Too Many Requests`: Rate limit exceeded

**Example**:
```bash
curl -X DELETE http://localhost:8080/api/v1/documents/doc_123
```

#### Upload Documents (Batch)

Upload multiple documents in a single request.

**Endpoint**: `POST /api/v1/documents/batch`

**Request Body**:
```json
{
  "documents": [
    {
      "filename": "doc1.pdf",
      "content": "base64_content_1",
      "content_type": "application/pdf"
    },
    {
      "filename": "doc2.txt",
      "content": "base64_content_2",
      "content_type": "text/plain"
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "doc1.pdf",
      "chunk_count": 10
    },
    {
      "id": "doc_124",
      "filename": "doc2.txt",
      "chunk_count": 5
    }
  ],
  "errors": [],
  "total": 2,
  "success_count": 2,
  "error_count": 0
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `429 Too Many Requests`: Rate limit exceeded

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/documents/batch \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "filename": "doc1.txt",
        "content": "VGhpcyBpcyBkb2Mx",
        "content_type": "text/plain"
      }
    ]
  }'
```

---

### Queries

#### Process Query

Process a query and return an answer using RAG.

**Endpoint**: `POST /api/v1/queries`

**Request Body**:
```json
{
  "query": "What is Python?",
  "top_k": 5,
  "score_threshold": 0.7,
  "stream": false
}
```

**Parameters**:
- `query` (string, required): User query (1-5000 characters)
- `top_k` (integer, optional): Number of results to retrieve (1-20, default: 5)
- `score_threshold` (float, optional): Minimum similarity score (0.0-1.0, default: 0.3)
- `stream` (boolean, optional): Enable streaming response (default: false)

**Response**: `200 OK`
```json
{
  "answer": "Python is a high-level programming language...",
  "sources": [
    {
      "chunk_id": "chunk_1",
      "content": "Python is a programming language...",
      "source": "doc_123",
      "score": 0.95
    }
  ],
  "score": 0.95,
  "metadata": {}
}
```

**Error Responses**:
- `400 Bad Request`: Invalid query or parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Special Response** (when no documents indexed):
```json
{
  "answer": "No documents are indexed in the knowledge base. Please upload at least one document before making queries.",
  "sources": [],
  "score": 0.0,
  "metadata": {
    "error": "no_documents",
    "message": "No documents have been indexed yet"
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "top_k": 5,
    "score_threshold": 0.7
  }'
```

---

### Agents

#### Chat with Agent (Streaming)

Chat with the agent using Server-Sent Events (SSE) for streaming responses.

**Endpoint**: `POST /api/v1/agents/chat`

**Request Body**:
```json
{
  "query": "What is Python?",
  "top_k": 5,
  "score_threshold": 0.7,
  "stream": true
}
```

**Parameters**: Same as Process Query endpoint

**Response**: `200 OK` (Streaming, `text/event-stream`)

The response is a stream of SSE events:

```
data: {"node": "retrieve", "state": {"query": "What is Python?"}}

data: {"node": "generate", "state": {"response": "Python is..."}}

data: {"node": "finalize", "state": {"response": "Python is a programming language."}}

data: [DONE]
```

**Error Responses**:
- `400 Bad Request`: Invalid query or parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "stream": true
  }' \
  --no-buffer
```

---

### Health

#### Health Check

Check the health status of the API.

**Endpoint**: `GET /api/v1/health`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-23T10:00:00Z"
}
```

**Example**:
```bash
curl http://localhost:8080/api/v1/health
```

#### Debug Info

Get debug information about the knowledge base (only available when `DEBUG=true`).

**Endpoint**: `GET /api/v1/health/debug`

**Response**: `200 OK` (when DEBUG=true)
```json
{
  "status": "ok",
  "collection_count": 100,
  "test_query_results": 5,
  "collection_name": "documents",
  "chroma_path": "./data/chroma"
}
```

**Error Responses**:
- `403 Forbidden`: Debug mode is not enabled

**Example**:
```bash
curl http://localhost:8080/api/v1/health/debug
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request parameters
- `403 Forbidden`: Access denied (e.g., debug endpoint)
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Rate Limit Headers

When rate limiting is enabled, responses include the following headers:

- `X-RateLimit-Limit`: Maximum number of requests allowed
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

---

## Content Types

### Supported Document Types

- **PDF**: `application/pdf` (uses Docling for advanced parsing)
- **DOCX**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Text**: `text/plain`
- **Markdown**: `text/markdown`

### Request/Response Formats

- **Request**: `application/json`
- **Response**: `application/json` (except streaming endpoints which use `text/event-stream`)

---

## Examples

### Complete Workflow

1. **Upload a document**:
```bash
curl -X POST http://localhost:8080/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "python_guide.txt",
    "content": "VGhpcyBpcyBhIGd1aWRlIGFib3V0IFB5dGhvbi4gUHl0aG9uIGlzIGEgcHJvZ3JhbW1pbmcgbGFuZ3VhZ2Uu",
    "content_type": "text/plain"
  }'
```

2. **Query the knowledge base**:
```bash
curl -X POST http://localhost:8080/api/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "top_k": 5
  }'
```

3. **List all documents**:
```bash
curl http://localhost:8080/api/v1/documents
```

4. **Delete a document**:
```bash
curl -X DELETE http://localhost:8080/api/v1/documents/doc_123
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

These interfaces allow you to:
- View all available endpoints
- See request/response schemas
- Test endpoints directly from the browser
- View example requests and responses

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Base64 encoding is required for binary content (PDF, DOCX)
- Maximum file size: ~50MB (base64 encoded)
- Rate limits are per IP address
- Streaming responses require proper SSE client handling
