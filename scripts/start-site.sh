#!/bin/bash
echo "🔧 Ativando Node.js 20..."
source ~/.nvm/nvm.sh 2>/dev/null || true
nvm use 20 2>/dev/null || echo "⚠️  nvm não encontrado. Instale Node.js 20 manualmente."

echo ""
echo "✅ Node.js versão: $(node -v 2>&1)"
echo ""

cd frontend

echo "🧹 Limpando instalação anterior..."
rm -rf node_modules package-lock.json .next 2>/dev/null || true

echo "📦 Instalando dependências..."
npm install

echo ""
echo "🚀 Iniciando servidor na porta 3001..."
echo "   Acesse: http://localhost:3001"
echo ""

npm run dev -- -p 3001
