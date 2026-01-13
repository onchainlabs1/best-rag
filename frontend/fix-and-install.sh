#!/bin/bash
# Script para corrigir permissões e instalar dependências

set -e

echo "🔧 Corrigindo problemas de permissão e instalando dependências..."
echo ""

# Carregar nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Usar Node.js 20
echo "📦 Ativando Node.js 20..."
nvm use 20 > /dev/null 2>&1 || nvm use 20.1.0

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# Corrigir permissões do cache do npm (se possível)
echo "🔐 Tentando corrigir permissões do cache npm..."
if [ -d "$HOME/.npm" ]; then
    echo "   Executando: sudo chown -R $(id -u):$(id -g) \"$HOME/.npm\""
    echo "   (Você precisará digitar sua senha)"
    sudo chown -R $(id -u):$(id -g) "$HOME/.npm" 2>/dev/null || {
        echo "   ⚠️  Não foi possível corrigir permissões automaticamente"
        echo "   Execute manualmente: sudo chown -R $(id -u):$(id -g) \"$HOME/.npm\""
    }
fi

# Limpar cache
echo ""
echo "🧹 Limpando cache..."
npm cache clean --force 2>/dev/null || true

# Remover node_modules e lock files
echo ""
echo "🗑️  Removendo node_modules e arquivos de lock..."
rm -rf node_modules package-lock.json yarn.lock 2>/dev/null || true

# Instalar dependências
echo ""
echo "📥 Instalando dependências..."
echo "   (Isso pode levar alguns minutos...)"
npm install --legacy-peer-deps

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🚀 Para iniciar o servidor:"
echo "   PORT=3001 npm run dev"
echo ""
echo "Ou use o script:"
echo "   bash start.sh"
