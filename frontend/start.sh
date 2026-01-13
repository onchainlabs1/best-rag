#!/bin/bash
# Script para iniciar o frontend com Node.js correto

set -e

echo "🔧 Configurando ambiente Node.js..."

# Carregar nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Usar Node.js 20
echo "📦 Ativando Node.js 20..."
nvm use 20 > /dev/null 2>&1 || nvm use 20.1.0

# Verificar versão
echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências..."
    # Tentar yarn primeiro (evita problemas de permissão)
    if command -v yarn &> /dev/null; then
        echo "   Usando yarn..."
        yarn install
    else
        echo "   Usando npm..."
        npm install
    fi
else
    echo "✅ Dependências já instaladas"
fi

# Criar .env.local se não existir
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
    echo "PORT=3001" >> .env.local
    echo "✅ Arquivo .env.local criado"
fi

# Iniciar servidor
echo ""
echo "🚀 Iniciando servidor na porta 3001..."
echo "📍 Acesse: http://localhost:3001"
echo ""

# Usar yarn se disponível, senão npm
if command -v yarn &> /dev/null && [ -f "yarn.lock" ]; then
    PORT=3001 yarn dev
else
    PORT=3001 npm run dev
fi
