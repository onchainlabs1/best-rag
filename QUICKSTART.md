# Quick Start - Testar Localmente

Guia rápido para testar o projeto localmente em portas livres.

## 🚀 Opção 1: Com Docker (Mais Fácil)

### Iniciar todos os serviços

```bash
./scripts/dev.sh
```

Ou manualmente:

```bash
# Definir portas (opcional, usa padrão se não definir)
export BACKEND_PORT=8080
export FRONTEND_PORT=3001

# Iniciar serviços
docker compose up --build

# Ou se usar docker-compose (versão antiga):
docker-compose up --build
```

**Acessos:**
- API: http://localhost:8080/docs
- Frontend: http://localhost:3001
- Health Check: http://localhost:8080/api/v1/health

### Iniciar apenas o Frontend localmente (sem Docker) ⭐ RECOMENDADO

**Método mais fácil:**
```bash
./scripts/start-frontend.sh
```

O frontend estará em: **http://localhost:3001**

**Ou manualmente:**
```bash
cd frontend
npm install  # Apenas na primeira vez
npm run dev -- -p 3001
```

**Veja `RUN-FRONTEND.md` para guia completo.**

### Ver logs

```bash
docker-compose logs -f
```

### Parar serviços

```bash
docker-compose down
```

## 🧪 Opção 2: Backend Localmente (Sem Docker)

### Pré-requisitos

- Python 3.11+
- Poetry instalado

### Instalar e executar

```bash
./scripts/test-local.sh
```

Ou manualmente:

```bash
cd backend

# Instalar dependências
poetry install

# Copiar variáveis de ambiente
cp .env.example .env  # Configure suas variáveis

# Iniciar servidor na porta 8080
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

**Acesso:**
- API: http://localhost:8080/docs

## 📋 Portas Padrão

| Serviço | Porta | URL |
|---------|-------|-----|
| Backend | 8080 | http://localhost:8080 |
| Frontend | 3001 | http://localhost:3001 |
| PostgreSQL | 5433 | localhost:5433 |
| ChromaDB | 8002 | http://localhost:8002 |

## ⚙️ Mudar Portas

Crie um arquivo `.env.local` na raiz:

```bash
BACKEND_PORT=9090      # Mude para outra porta
FRONTEND_PORT=3002     # Mude para outra porta
POSTGRES_PORT=5434     # Mude se 5433 estiver em uso
CHROMA_PORT=8003       # Mude se 8002 estiver em uso
```

Ou exporte as variáveis:

```bash
export BACKEND_PORT=9090
./scripts/dev.sh
```

## 🐛 Frontend não está funcionando?

Se o frontend não estiver acessível no Docker, tente rodar localmente:

```bash
./scripts/start-frontend.sh

# Ou manualmente:
cd frontend
npm install
npm run dev -- -p 3001
```

Veja `TROUBLESHOOTING.md` para mais soluções.

## ✅ Verificar se Funcionou

1. **Testar API:**
   ```bash
   curl http://localhost:8080/api/v1/health
   ```

2. **Acessar documentação:**
   - Abra: http://localhost:8080/docs
   - Deve mostrar a interface Swagger

3. **Testar upload de documento:**
   - Use a interface Swagger ou
   - Frontend em http://localhost:3001

## 🐛 Troubleshooting

### Porta já em uso

Verifique portas em uso:
```bash
lsof -i :8080
lsof -i :3001
```

Mude as portas no `.env.local` ou exporte variáveis.

### Docker não inicia

Verifique se Docker está rodando:
```bash
docker info
```

### Dependências faltando

No backend:
```bash
cd backend
poetry install
```

No frontend:
```bash
cd frontend
npm install
```

## 📚 Mais Informações

- Ver `README.md` para documentação completa
- Ver `PORTS.md` para detalhes sobre portas
- Ver `ARCHITECTURE.md` para arquitetura do sistema
