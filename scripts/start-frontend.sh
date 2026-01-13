#!/bin/bash
# Script para iniciar apenas o frontend localmente

set -e

echo "🎨 Iniciando Frontend localmente..."

# Verifica se está no diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d "frontend" ]; then
    echo "❌ Diretório frontend não encontrado. Execute este script a partir do diretório raiz do projeto."
    exit 1
fi

cd frontend

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não está instalado. Instale Node.js 18+ primeiro."
    echo "   Baixe em: https://nodejs.org/"
    exit 1
fi

# Verifica versão do Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js versão $NODE_VERSION detectada. Recomendado: Node.js 18+"
    read -p "Continuar mesmo assim? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verifica se npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm não está instalado."
    exit 1
fi

# Verifica se node_modules existe ou se package.json foi modificado
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
    echo "✅ Dependências instaladas"
fi

# Define porta padrão
FRONTEND_PORT=${FRONTEND_PORT:-3001}
BACKEND_PORT=${BACKEND_PORT:-8080}

# Carrega .env.local se existir (da raiz do projeto)
if [ -f "../.env.local" ]; then
    export $(cat ../.env.local | grep -v '^#' | xargs)
    FRONTEND_PORT=${FRONTEND_PORT:-3001}
    BACKEND_PORT=${BACKEND_PORT:-8080}
fi

export NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}

echo ""
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "   Frontend: http://localhost:${FRONTEND_PORT}"
echo "   API URL: ${NEXT_PUBLIC_API_URL}"
echo "   Node.js: $(node -v)"
echo "   npm: $(npm -v)"
echo ""
echo "💡 Pressione Ctrl+C para parar"
echo ""

# Inicia servidor Next.js na porta especificada (padrão 3001)
echo "🚀 Iniciando na porta ${FRONTEND_PORT}..."
exec npm run dev -- -p ${FRONTEND_PORT} -H 0.0.0.0
