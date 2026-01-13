#!/bin/bash
# Script para iniciar o frontend em porta diferente (3001)

set -e

echo "🎨 Iniciando Frontend RAG + Agent Knowledge Base"
echo ""

cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

# Criar .env.local se não existir
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
    echo "PORT=3001" >> .env.local
    echo "✅ Arquivo .env.local criado"
fi

echo "🚀 Iniciando servidor na porta 3001..."
echo "📍 Acesse: http://localhost:3001"
echo ""

# Iniciar na porta 3001
PORT=3001 NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
