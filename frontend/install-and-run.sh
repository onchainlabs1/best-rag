#!/bin/bash
# Script para instalar e rodar o frontend

set -e

echo "🔧 Ativando Node.js 20..."
source ~/.nvm/nvm.sh 2>/dev/null || true
nvm use 20 2>/dev/null || {
    echo "❌ nvm não encontrado. Execute: source ~/.nvm/nvm.sh"
    exit 1
}

echo "✅ Node.js: $(node -v)"
echo "✅ npm: $(npm -v)"
echo ""

cd "$(dirname "$0")"

echo "🧹 Limpando cache do npm..."
npm cache clean --force 2>/dev/null || true

echo "📦 Instalando dependências..."
echo "   Isso pode levar 1-3 minutos..."
echo ""

# Tenta instalar com diferentes flags
npm install --legacy-peer-deps --prefer-offline --no-audit 2>&1 | grep -E "(added|up to date|ERR)" || npm install --legacy-peer-deps 2>&1 | tail -20

echo ""
echo "🚀 Iniciando servidor na porta 3001..."
echo "   Acesse: http://localhost:3001"
echo ""

npm run dev -- -p 3001
