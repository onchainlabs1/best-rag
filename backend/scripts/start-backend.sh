#!/bin/bash
# Script para iniciar o backend localmente

set -e

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script do diretório backend/"
    exit 1
fi

# Verificar se venv existe
if [ ! -d ".venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado. Execute primeiro: ./scripts/setup.sh"
    exit 1
fi

# Ativar venv
source .venv/bin/activate

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando..."
    # Tentar copiar de .env.example ou env.example.txt
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado a partir de .env.example"
    elif [ -f "env.example.txt" ]; then
        cp env.example.txt .env
        echo "✅ Arquivo .env criado a partir de env.example.txt"
    else
        echo "⚠️  Template não encontrado. Criando .env com configurações padrão..."
        # Criar .env básico usando printf para evitar problemas de redirecionamento
        printf "# Vector Database - caminho local\n" > .env
        printf "CHROMA_PATH=./data/chroma\n\n" >> .env
        printf "# LLM Providers\n" >> .env
        printf "LLM_PROVIDER=local\n" >> .env
        printf "LLM_MODEL=gpt-4-turbo-preview\n\n" >> .env
        printf "# Embeddings - usar modelo local (não precisa API key)\n" >> .env
        printf "EMBEDDING_PROVIDER=local\n" >> .env
        printf "LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2\n\n" >> .env
        printf "# App Settings\n" >> .env
        printf "DEBUG=true\n" >> .env
        printf "LOG_LEVEL=INFO\n" >> .env
        echo "✅ Arquivo .env criado com configurações padrão"
    fi
fi

# Criar diretórios se não existirem
mkdir -p data/chroma
mkdir -p logs

# Iniciar servidor
echo "🚀 Iniciando servidor FastAPI..."
echo "📍 Acesse: http://localhost:8080/docs"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
