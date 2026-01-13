# Configuração de Portas

Este projeto usa portas configuráveis para evitar conflitos com outros serviços.

## Portas Padrão

- **Backend (FastAPI)**: `8080` → API em `http://localhost:8080`
- **Frontend (Next.js)**: `3001` → UI em `http://localhost:3001`
- **PostgreSQL**: `5433` → Banco de dados
- **ChromaDB**: `8002` → Vector database

## Configuração

### Opção 1: Variáveis de Ambiente (Recomendado)

Crie um arquivo `.env.local` na raiz do projeto:

```bash
BACKEND_PORT=8080
FRONTEND_PORT=3001
POSTGRES_PORT=5433
CHROMA_PORT=8002
```

O Docker Compose carregará automaticamente essas variáveis.

### Opção 2: Exportar Variáveis

```bash
export BACKEND_PORT=8080
export FRONTEND_PORT=3001
export POSTGRES_PORT=5433
export CHROMA_PORT=8002
docker-compose up
```

### Opção 3: Usar Portas Padrão

Se você não configurar nada, as portas padrão serão usadas (8080, 3001, 5433, 8002).

## Mudar Portas

Se alguma porta estiver em uso, ajuste as variáveis de ambiente:

```bash
# Exemplo: usar porta 9090 para backend
export BACKEND_PORT=9090
./scripts/dev.sh
```

## Verificar Portas em Uso

```bash
# Ver portas em uso
lsof -i -P | grep LISTEN | grep -E "(8080|3001|5433|8002)"

# Ou verificar porta específica
lsof -i :8080
```

## URLs dos Serviços

- **API Documentation**: http://localhost:8080/docs
- **API Health Check**: http://localhost:8080/api/v1/health
- **Frontend**: http://localhost:3001
