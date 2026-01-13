#!/bin/bash
# Script de setup para desenvolvimento local

set -e

echo "🚀 Configurando ambiente de desenvolvimento local..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python encontrado: $(python3 --version)"

# Criar venv se não existir
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar venv e instalar dependências
echo "📥 Instalando dependências..."
source .venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel --no-cache-dir

# Instalar dependências
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --no-cache-dir
else
    echo "⚠️  requirements.txt não encontrado. Criando a partir do pyproject.toml..."
    # Se poetry funcionar, usar poetry
    if command -v poetry &> /dev/null; then
        poetry install
    else
        echo "❌ Poetry não encontrado e requirements.txt não existe"
        exit 1
    fi
fi

# Criar diretórios necessários
echo "📁 Criando diretórios de dados..."
mkdir -p data/chroma
mkdir -p logs

# Copiar .env se não existir
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Copiando .env.example para .env..."
        cp .env.example .env
        echo "✅ Arquivo .env criado. Por favor, ajuste as variáveis se necessário."
    elif [ -f "env.example.txt" ]; then
        echo "📋 Copiando env.example.txt para .env..."
        cp env.example.txt .env
        echo "✅ Arquivo .env criado. Por favor, ajuste as variáveis se necessário."
    else
        echo "⚠️  Template .env não encontrado (.env.example ou env.example.txt)"
        echo "   Criando .env básico..."
        printf "# Vector Database\nCHROMA_PATH=./data/chroma\n\n# LLM\nLLM_PROVIDER=local\nLLM_MODEL=gpt-4-turbo-preview\n\n# Embeddings\nEMBEDDING_PROVIDER=local\nLOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2\n\n# App\nDEBUG=true\nLOG_LEVEL=INFO\n" > .env
        echo "✅ Arquivo .env criado com configurações padrão"
    fi
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "Para iniciar o servidor:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload"
echo ""
echo "Ou use o script:"
echo "  ./scripts/start-backend.sh"
