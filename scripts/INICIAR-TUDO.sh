#!/bin/bash
# Script para iniciar backend e frontend juntos

set -e

echo "🚀 Iniciando RAG + Agent Knowledge Base System"
echo ""

# Verificar se estamos na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Execute este script da raiz do projeto"
    exit 1
fi

# Função para verificar se uma porta está em uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Porta em uso
    else
        return 1  # Porta livre
    fi
}

# Verificar portas
echo "🔍 Verificando portas..."
if check_port 8080; then
    echo "⚠️  Porta 8080 (backend) já está em uso"
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

if check_port 3000; then
    echo "⚠️  Porta 3000 (frontend) já está em uso"
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo ""

# Iniciar Backend
echo "📦 Iniciando Backend..."
cd backend

if [ ! -d ".venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado. Execute primeiro:"
    echo "   cd backend && ./scripts/setup.sh"
    exit 1
fi

# Iniciar backend em background
./scripts/start-backend.sh > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend iniciado (PID: $BACKEND_PID)"
echo "   Logs: logs/backend.log"
echo "   API: http://localhost:8080/docs"

# Aguardar backend iniciar
echo "⏳ Aguardando backend iniciar..."
sleep 5

# Verificar se backend está respondendo
if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend está respondendo"
else
    echo "⚠️  Backend pode não estar pronto ainda"
fi

cd ..

# Iniciar Frontend
echo ""
echo "🎨 Iniciando Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "⚠️  Dependências não instaladas. Instalando..."
    npm install
fi

# Criar .env.local se não existir
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
    echo "✅ Arquivo .env.local criado"
fi

# Iniciar frontend em background
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
echo "   Logs: logs/frontend.log"
echo "   Interface: http://localhost:3000"

cd ..

# Criar diretório de logs se não existir
mkdir -p logs

echo ""
echo "✅ Sistema iniciado!"
echo ""
echo "📍 Acesse:"
echo "   - Interface: http://localhost:3000"
echo "   - API Docs: http://localhost:8080/docs"
echo ""
echo "📋 Para parar:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   tail -f logs/backend.log"
echo "   tail -f logs/frontend.log"
