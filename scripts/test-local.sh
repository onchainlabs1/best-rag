#!/bin/bash
# Script para testar localmente sem Docker

set -e

echo "🧪 Testando localmente..."

# Verifica se está no diretório correto
if [ ! -d "backend" ]; then
    echo "❌ Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

cd backend

# Verifica se Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry não está instalado. Instale com: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Instala dependências se necessário
if [ ! -d ".venv" ]; then
    echo "📦 Instalando dependências..."
    poetry install
fi

# Ativa ambiente virtual
source .venv/bin/activate

# Carrega variáveis de ambiente
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Arquivo .env não encontrado. Criando .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado. Configure suas variáveis de ambiente."
    fi
fi

# Define porta do backend (evita conflito com porta 8000 em uso)
BACKEND_PORT=${BACKEND_PORT:-8080}
export PORT=${BACKEND_PORT}

echo ""
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "   Porta: ${BACKEND_PORT}"
echo "   API: http://localhost:${BACKEND_PORT}/docs"
echo ""
echo "💡 Pressione Ctrl+C para parar"
echo ""

# Inicia servidor
poetry run uvicorn src.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload
