#!/bin/bash
# Script para corrigir ambiente virtual e reinstalar dependências

set -e

echo "🔧 Corrigindo ambiente virtual..."

cd "$(dirname "$0")/.." || exit 1

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script do diretório backend/"
    exit 1
fi

# Remover venv antigo se existir
if [ -d ".venv" ]; then
    echo "🗑️  Removendo ambiente virtual antigo..."
    rm -rf .venv
fi

# Criar novo venv
echo "📦 Criando novo ambiente virtual..."
python3 -m venv .venv

# Ativar venv
echo "✅ Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar que estamos usando o Python correto
echo "🐍 Python sendo usado: $(which python)"
echo "📍 Versão: $(python --version)"

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip setuptools wheel --no-cache-dir

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt --no-cache-dir

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
python -c "import fastapi; print('✅ fastapi')" 2>/dev/null || echo "❌ fastapi"
python -c "import langchain_text_splitters; print('✅ langchain-text-splitters')" 2>/dev/null || echo "❌ langchain-text-splitters"
python -c "import chromadb; print('✅ chromadb')" 2>/dev/null || echo "❌ chromadb"
python -c "import langchain; print('✅ langchain')" 2>/dev/null || echo "❌ langchain"

echo ""
echo "✅ Ambiente virtual corrigido!"
echo ""
echo "Para usar:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload"
