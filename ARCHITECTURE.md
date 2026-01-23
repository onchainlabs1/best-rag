# Architecture Documentation

This document provides detailed architecture information for AI agents working on this project.

## System Overview

A Knowledge Base system that:
- Accepts document uploads (PDF, TXT, MD, etc.)
- Indexes documents using vector embeddings
- Uses RAG (Retrieval-Augmented Generation) for semantic search
- Employs LangGraph agents for intelligent query processing
- Provides REST API and web interface

## Architecture Layers

### 1. Data Layer
- **ChromaDB**: Vector database for embeddings and document storage (persistent, local file-based)
- **SQLite**: Document metadata stored persistently in SQLite database (DocumentStorage) - default for development
- **PostgreSQL**: Alternative storage backend for production (PostgreSQLDocumentStorage) - configurable via `STORAGE_BACKEND`

### 2. RAG Layer (`backend/src/rag/`)
- **Chunking**: Intelligent document splitting with overlap (RecursiveCharacterTextSplitter)
- **Embeddings**: Generation via OpenAI or local models (configurable via `EMBEDDING_PROVIDER`)
- **Retriever**: Vector similarity search using ChromaDB (semantic search)
- **Vector Store**: ChromaDB integration for persistent storage
- **Hybrid Search**: BM25 + Vector search combination (configurable via `SEARCH_TYPE`)
- **Re-ranking**: Cross-Encoder re-ranking for improved result quality (configurable via `RERANK_ENABLED`)
- **Caching**: TTL-based caching for embeddings and queries (configurable via `CACHE_ENABLED`)
- **Query Expansion**: LLM-based query expansion for improved recall (configurable via `QUERY_EXPANSION_ENABLED`)

### 3. Agent Layer (`backend/src/agents/`)
- **LangGraph**: State graph with typed state management
- **Nodes**: retrieve → generate → validate → refine → finalize
- **State**: Typed with TypedDict (query, context, response, validation_score)
- **LLM Support**: Groq (default), OpenAI, Anthropic (configurable via `LLM_PROVIDER`)
- **Checkpointing**: Optional state persistence using SQLite (configurable via `CHECKPOINTING_ENABLED`)

### 4. Service Layer (`backend/src/services/`)
- **DocumentService**: Document upload, processing, indexing
- **AgentService**: Agent orchestration, state management

### 5. API Layer (`backend/src/api/`)
- **FastAPI**: REST API with OpenAPI/Swagger
- **Routes**: `/api/v1/documents`, `/api/v1/queries`, `/api/v1/agents/chat`
- **Streaming**: SSE for agent responses

### 6. Frontend (`frontend/`)
- **Next.js 15**: React with App Router
- **TypeScript**: Type safety
- **Tailwind + Shadcn/ui**: Modern UI components

## Data Flow

```
User Upload → Chunking → Embeddings → Vector DB
User Query → Agent → Retrieve (RAG) → Generate → Validate → Response
```

## Key Design Decisions

1. **Spec-Driven**: All code follows Type Specs → Test Specs → Implementation
2. **Type Safety**: Pydantic schemas as contracts, mypy strict mode
3. **Modular**: Each layer independent with clear interfaces
4. **Observable**: Structured logging (OpenTelemetry tracing planned)
5. **Agent-Friendly**: Small modules, clear contracts, self-documenting

## Dependencies Between Modules

- `agents/` depends on `rag/` (uses retriever)
- `api/` depends on `services/` (uses business logic)
- `services/` depends on `models/` and `rag/`
- All depend on `schemas/` (Type Specs)

## Configuration

Configuration via `pydantic-settings`:
- Environment variables in `.env`
- Type-safe config in `config.py`
- Secrets management for API keys

## Testing Strategy

1. **Unit Tests**: Each module tested independently
2. **Integration Tests**: API endpoints, RAG pipeline
3. **Fixtures**: Reusable test data and mocks
4. **Coverage**: Minimum 80% enforced in CI

## Development Workflow

1. Define Type Specs (Pydantic schemas)
2. Write Test Specs (pytest)
3. Implement functionality
4. Validate (mypy + pytest)
5. Integrate with other modules
