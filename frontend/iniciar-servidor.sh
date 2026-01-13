#!/bin/bash
# Script simples para iniciar o servidor frontend

cd "$(dirname "$0")"

echo "🔧 Configurando ambiente..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20 > /dev/null 2>&1

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules não encontrado!"
    echo "   Execute primeiro: bash fix-and-install.sh"
    exit 1
fi

# Verificar se next está instalado
if ! command -v next &> /dev/null && [ ! -f "node_modules/.bin/next" ]; then
    echo "❌ Next.js não encontrado!"
    echo "   Execute: npm install"
    exit 1
fi

# Criar .env.local se não existir
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
    echo "PORT=3001" >> .env.local
fi

echo "🚀 Iniciando servidor na porta 3001..."
echo "📍 Acesse: http://localhost:3001"
echo ""
echo "⚠️  Pressione Ctrl+C para parar o servidor"
echo ""

# Usar npx para garantir que usa o next local
PORT=3001 npx next dev
