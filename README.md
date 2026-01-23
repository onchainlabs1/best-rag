# RAG + Agent Knowledge Base System

> **🎯 Reference Implementation**: This project demonstrates **modern engineering practices** and **solid RAG architecture** for building production knowledge base systems. It showcases Spec-Driven Development, type safety, and modern AI/ML integration patterns.

A modern Knowledge Base system using RAG (Retrieval-Augmented Generation) with autonomous agents built in Python, following **Spec-Driven Development (SDD)** principles.

## 🎯 Overview

This project demonstrates **best practices in software engineering** and **modern RAG architecture**, featuring:

- **Spec-Driven Development**: Type Specs → Test Specs → Implementation
- **Type Safety**: 100% type hints, mypy strict mode, Pydantic validation
- **Modern RAG Stack**: LangGraph agents, ChromaDB vector store, multi-provider LLM support
- **Production-Ready Architecture**: FastAPI backend, Next.js frontend, Docker support
- **Solid Foundation**: Well-structured codebase ready for advanced RAG features

### What This Project Is

✅ **Best Practices Implemented:**
- Spec-Driven Development (SDD)
- Complete type safety (mypy strict mode)
- Modern agent architecture (LangGraph)
- Production-ready code structure
- Structured logging and error handling
- Multi-provider LLM support

✅ **RAG Features Implemented:**
- Vector-based semantic search (ChromaDB)
- Intelligent document chunking with overlap
- Multi-provider embeddings (OpenAI/local)
- LangGraph agents with multi-step reasoning
- Advanced PDF parsing (Docling)
- Streaming responses (SSE)

🚧 **Advanced RAG Features (Planned):**
- Hybrid search (BM25 + vector)
- Re-ranking with Cross-Encoder
- Query expansion
- Advanced observability (OpenTelemetry)
- Caching layer

**This is a solid foundation** for RAG systems, demonstrating best practices in code architecture, type safety, and agent orchestration. Use this as a reference when building production RAG systems.

## 🏗️ Architecture

- **Backend**: FastAPI + LangGraph + LangChain
- **RAG**: Intelligent chunking, embeddings (OpenAI/local), vector search (ChromaDB)
- **Agents**: LangGraph with state management and multi-step reasoning
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (or pip)
- Docker & Docker Compose (optional)
- Node.js 18+ (for frontend)

### Backend Setup

```bash
cd backend
poetry install
# or: pip install -r requirements.txt

# Copy environment template
cp env.example.txt .env

# Edit .env and add your API keys:
# GROQ_API_KEY=your_key_here
# LLM_PROVIDER=groq
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended)

```bash
docker compose up -d
```

**Default Ports:**
- Backend: `http://localhost:8080`
- Frontend: `http://localhost:3001`
- API Docs: `http://localhost:8080/docs`

## 📚 Methodology: Spec-Driven Development

This project follows **Spec-Driven Development**:

1. **Type Specs**: Pydantic schemas define contracts (`schemas/`)
2. **Test Specs**: pytest tests specify behavior (`tests/`)
3. **Implementation**: Code implements the specs (`src/`)
4. **Validation**: mypy + pytest verify specs are met

## 🧪 Development

### Run Tests

```bash
make test
# or
cd backend && poetry run pytest
```

### Linting & Type Checking

```bash
make lint      # Ruff linter
make type-check # mypy type checker
make format    # Format code
```

### Start Development Server

```bash
# With Docker
./scripts/dev.sh

# Or locally
cd backend
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

## 📖 Project Structure

```
backend/
  src/
    agents/       # LangGraph agents (state, nodes, graph)
    rag/          # RAG system (chunking, embeddings, retriever)
    schemas/      # Pydantic schemas (Type Specs)
    api/          # FastAPI routes
    services/     # Business logic
  tests/          # Test Specs (pytest)
```

## 🔌 API Endpoints

- `POST /api/v1/documents` - Upload documents
- `GET /api/v1/documents` - List documents
- `DELETE /api/v1/documents/{id}` - Delete document
- `POST /api/v1/queries` - Process queries (non-streaming)
- `POST /api/v1/agents/chat` - Chat with streaming (SSE)
- `GET /api/v1/health` - Health check

See `API.md` for detailed API documentation and examples.

## ⚙️ Configuration

Configure via environment variables (`.env` file):

```bash
# LLM Provider (groq, openai, anthropic)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your_key

# Embeddings (openai, local)
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Database
CHROMA_PATH=./data/chroma
```

See `backend/env.example.txt` for all available options.

## 🧪 Testing

All tests follow Spec-Driven Development:

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# With coverage
poetry run pytest --cov=src --cov-report=html
```

## 🔒 Security

- API keys stored in `.env` (not committed)
- CORS configurable (default: open for development)
- Debug endpoint available (disable in production)
- Rate limiting: Implemented (configurable via environment variables)

See `SECURITY.md` for security best practices.

## 📦 Features

### Implemented ✅
- Document upload (PDF, TXT, MD, DOCX)
- Vector embeddings (OpenAI/local)
- Semantic search (ChromaDB)
- **Hybrid search** (BM25 + Vector) - configurable
- **Re-ranking** with Cross-Encoder - configurable
- **Query expansion** using LLM - configurable
- **Caching** for embeddings and queries - configurable
- LangGraph agents with multi-step reasoning
- Streaming responses (SSE)
- Type-safe APIs (Pydantic)
- Structured logging
- **Rate limiting** - configurable
- **PostgreSQL support** - alternative to SQLite
- **Checkpointing** - optional state persistence
- **OpenTelemetry tracing** - for observability

### Planned (Not Yet Implemented) 🚧
- Multi-modal support
- Advanced metadata filtering

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.

## 📄 License

MIT License - see `LICENSE` file for details.

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [FastAPI](https://fastapi.tiangolo.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Next.js](https://nextjs.org/)

## 📚 Documentation

- `ARCHITECTURE.md` - System architecture
- `BEST-PRACTICES.md` - **Best practices showcase** (what's implemented and why)
- `QUICKSTART.md` - Quick start guide
- `API.md` - API documentation
- `DEPLOYMENT.md` - Free deployment guide (Vercel, Render, Fly.io)
- `QUICK-DEPLOY.md` - 5-minute deployment guide
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security considerations
