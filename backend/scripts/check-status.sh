#!/bin/bash
# Script para verificar status do backend

set -e

echo "🔍 Verificando status do backend..."

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script do diretório backend/"
    exit 1
fi

# Verificar venv
if [ ! -d ".venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado"
    echo "   Execute: ./scripts/setup.sh"
else
    echo "✅ Ambiente virtual encontrado"
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado"
    echo "   Execute: cp .env.example .env"
else
    echo "✅ Arquivo .env encontrado"
fi

# Verificar diretórios
if [ ! -d "data/chroma" ]; then
    echo "⚠️  Diretório data/chroma não encontrado"
    mkdir -p data/chroma
    echo "   ✅ Criado"
else
    echo "✅ Diretório data/chroma existe"
fi

# Verificar dependências básicas
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo ""
    echo "📦 Verificando dependências principais..."
    
    python -c "import fastapi" 2>/dev/null && echo "✅ fastapi instalado" || echo "❌ fastapi não instalado"
    python -c "import uvicorn" 2>/dev/null && echo "✅ uvicorn instalado" || echo "❌ uvicorn não instalado"
    python -c "import pydantic" 2>/dev/null && echo "✅ pydantic instalado" || echo "❌ pydantic não instalado"
    python -c "import chromadb" 2>/dev/null && echo "✅ chromadb instalado" || echo "❌ chromadb não instalado"
    python -c "import langchain" 2>/dev/null && echo "✅ langchain instalado" || echo "❌ langchain não instalado"
    python -c "import langgraph" 2>/dev/null && echo "✅ langgraph instalado" || echo "❌ langgraph não instalado"
    python -c "import sentence_transformers" 2>/dev/null && echo "✅ sentence-transformers instalado" || echo "❌ sentence-transformers não instalado"
fi

echo ""
echo "✅ Verificação concluída!"
