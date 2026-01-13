#!/bin/bash
# Script para reiniciar o backend

set -e

echo "🔄 Reiniciando servidor backend..."

cd "$(dirname "$0")"

# Parar processo existente na porta 8080
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "🛑 Parando servidor existente..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Verificar se venv existe
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "   Execute primeiro: ./scripts/setup.sh"
    exit 1
fi

# Ativar venv
source .venv/bin/activate

# Verificar se .env existe
if [ ! -f ".env" ]; then
    if [ -f "env.example.txt" ]; then
        cp env.example.txt .env
        echo "✅ Arquivo .env criado"
    fi
fi

# Criar diretórios se não existirem
mkdir -p data/chroma
mkdir -p logs

# Iniciar servidor
echo "🚀 Iniciando servidor FastAPI..."
echo "📍 Acesse: http://localhost:8080/docs"
echo ""
echo "⚠️  Pressione Ctrl+C para parar o servidor"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
