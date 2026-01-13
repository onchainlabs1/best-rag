#!/bin/bash
# Script para iniciar o ambiente de desenvolvimento local

set -e

echo "🚀 Iniciando RAG + Agent Knowledge Base..."

# Verifica se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Carrega variáveis de ambiente (se existir .env.local)
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo "✅ Variáveis de ambiente carregadas de .env.local"
else
    echo "ℹ️  Arquivo .env.local não encontrado. Usando portas padrão."
    echo "   Crie .env.local para configurar portas personalizadas (veja PORTS.md)"
fi

# Define portas padrão se não estiverem definidas
export BACKEND_PORT=${BACKEND_PORT:-8080}
export FRONTEND_PORT=${FRONTEND_PORT:-3001}
export POSTGRES_PORT=${POSTGRES_PORT:-5433}
export CHROMA_PORT=${CHROMA_PORT:-8002}

echo ""
echo "📋 Configuração de Portas:"
echo "   Backend:    http://localhost:${BACKEND_PORT}"
echo "   Frontend:   http://localhost:${FRONTEND_PORT}"
echo "   PostgreSQL: localhost:${POSTGRES_PORT}"
echo "   Chroma:     http://localhost:${CHROMA_PORT}"
echo ""

# Cria diretório de dados se não existir
mkdir -p data

# Inicia serviços com Docker Compose
echo "🐳 Iniciando serviços com Docker Compose..."

# Tenta usar docker compose (novo) ou docker-compose (antigo)
if command -v docker &> /dev/null && docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Docker Compose não encontrado. Instale Docker Desktop ou docker-compose."
    exit 1
fi

echo "   Usando: $DOCKER_COMPOSE"
$DOCKER_COMPOSE up --build -d

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 5

# Verifica saúde dos serviços
echo ""
echo "🔍 Verificando saúde dos serviços..."
echo "   Aguardando 10 segundos para serviços iniciarem..."
sleep 10

# Verifica backend
if command -v curl > /dev/null 2>&1; then
    if curl -s http://localhost:${BACKEND_PORT}/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend está rodando em http://localhost:${BACKEND_PORT}"
        echo "   Docs: http://localhost:${BACKEND_PORT}/docs"
    else
        echo "⚠️  Backend ainda está iniciando..."
        echo "   Verifique os logs com: $DOCKER_COMPOSE logs backend"
    fi

    # Verifica frontend
    echo "   Aguardando mais 5 segundos para frontend..."
    sleep 5
    if curl -s http://localhost:${FRONTEND_PORT} > /dev/null 2>&1; then
        echo "✅ Frontend está rodando em http://localhost:${FRONTEND_PORT}"
    else
        echo "⚠️  Frontend ainda está iniciando ou pode ter erro..."
        echo "   Verifique os logs com: $DOCKER_COMPOSE logs frontend"
        echo "   Ou tente rodar localmente: ./scripts/start-frontend.sh"
    fi
else
    echo "ℹ️  curl não está instalado. Verifique manualmente:"
    echo "   Backend: http://localhost:${BACKEND_PORT}/docs"
    echo "   Frontend: http://localhost:${FRONTEND_PORT}"
fi

echo ""
echo "🎉 Ambiente iniciado com sucesso!"
echo ""
echo "📚 Próximos passos:"
echo "   1. Acesse a API: http://localhost:${BACKEND_PORT}/docs"
echo "   2. Acesse o Frontend: http://localhost:${FRONTEND_PORT}"
echo "   3. Para ver logs: $DOCKER_COMPOSE logs -f"
echo "   4. Para parar: $DOCKER_COMPOSE down"
echo ""
echo "💡 Se o frontend não funcionar no Docker, tente rodar localmente:"
echo "   ./scripts/start-frontend.sh"
echo ""
