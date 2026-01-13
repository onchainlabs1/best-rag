# Troubleshooting

Guia para resolver problemas comuns.

## Frontend não está acessível em http://localhost:3001

### Problema: Porta já em uso

**Solução:**
```bash
# Verificar porta em uso
lsof -i :3001

# Mudar porta no .env.local
export FRONTEND_PORT=3002
docker compose up --build
```

### Problema: Frontend não inicia no Docker

**Soluções:**

1. **Rebuild do frontend:**
```bash
docker compose build frontend --no-cache
docker compose up frontend
```

2. **Ver logs do frontend:**
```bash
docker compose logs -f frontend
```

3. **Iniciar frontend localmente (sem Docker):**
```bash
./scripts/start-frontend.sh

# Ou manualmente:
cd frontend
npm install
npm run dev -- -p 3001
```

### Problema: Dependências não instaladas

**Solução:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Problema: Erro "Cannot find module"

**Solução:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev -- -p 3001
```

## Backend não está acessível em http://localhost:8080

### Verificar se está rodando

```bash
# Com Docker
docker compose ps

# Ver logs
docker compose logs -f backend

# Testar health check
curl http://localhost:8080/api/v1/health
```

### Porta já em uso

```bash
# Verificar
lsof -i :8080

# Mudar porta
export BACKEND_PORT=9090
docker compose up --build
```

## Docker Compose não funciona

### Problema: "command not found: docker-compose"

**Solução:**
Use `docker compose` (sem hífen) - é o comando novo do Docker CLI:

```bash
docker compose up --build

# Se ainda não funcionar, instale Docker Compose standalone
# Ou use o script que detecta automaticamente:
./scripts/dev.sh
```

### Problema: "Cannot connect to Docker daemon"

**Solução:**
```bash
# Verificar se Docker está rodando
docker info

# Se não estiver, inicie o Docker Desktop ou:
sudo systemctl start docker  # Linux
```

## Dependências Python não instaladas

```bash
cd backend
poetry install

# Ou manualmente:
pip install -r requirements.txt  # Se tiver requirements.txt
```

## Variáveis de ambiente não carregadas

**Solução:**
```bash
# Criar .env.local na raiz do projeto
cat > .env.local << EOF
BACKEND_PORT=8080
FRONTEND_PORT=3001
POSTGRES_PORT=5433
CHROMA_PORT=8002
EOF

# Ou exportar manualmente
export BACKEND_PORT=8080
export FRONTEND_PORT=3001
docker compose up
```

## Erro de conexão com banco de dados

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
docker compose ps db

# Ver logs do banco
docker compose logs db

# Reiniciar banco
docker compose restart db
```

## Limpar tudo e recomeçar

```bash
# Parar todos os containers
docker compose down -v

# Limpar volumes
docker volume prune

# Rebuild tudo
docker compose build --no-cache
docker compose up
```

## Verificar status de todos os serviços

```bash
# Ver containers rodando
docker compose ps

# Ver logs de todos
docker compose logs -f

# Ver logs específicos
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

## Procurar erros específicos

```bash
# Backend
docker compose logs backend | grep -i error

# Frontend
docker compose logs frontend | grep -i error

# Todos os serviços
docker compose logs | grep -i error
```

## Testar serviços individualmente

### Testar Backend localmente
```bash
cd backend
poetry install
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### Testar Frontend localmente
```bash
cd frontend
npm install
npm run dev -- -p 3001
```

## API Keys Configuration

### Configure LLM Provider

The system supports multiple LLM providers. Configure in `backend/.env`:

**Groq (Recommended - Fast & Free):**
```bash
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
```

**OpenAI:**
```bash
OPENAI_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
```

**Anthropic:**
```bash
ANTHROPIC_API_KEY=your-anthropic-key
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
```

**Local (Mock - for testing):**
```bash
LLM_PROVIDER=local
```

### Configure Embeddings

**OpenAI Embeddings:**
```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-your-key
```

**Local Embeddings (No API key needed):**
```bash
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Create .env File

If `.env` doesn't exist:
```bash
cd backend
cp env.example.txt .env
# Edit .env and add your API keys
```

## Document Upload Issues

### PDF Not Parsing Correctly

The system uses Docling for advanced PDF parsing. If issues occur:

1. **Check Docling installation:**
   ```bash
   cd backend
   poetry run python -c "import docling; print('Docling OK')"
   ```

2. **Re-upload document** after parser improvements

3. **Check logs** for parsing errors:
   ```bash
   docker compose logs backend | grep -i docling
   ```

### No Documents Found After Upload

1. **Check ChromaDB:**
   ```bash
   curl http://localhost:8080/api/v1/health/debug
   ```

2. **Verify document was indexed:**
   ```bash
   curl http://localhost:8080/api/v1/documents
   ```

3. **Check score_threshold** - Lower it if needed (default: 0.3)

## Query Issues

### Generic or Poor Quality Responses

1. **Lower score_threshold** for more context:
   ```json
   {"query": "your question", "score_threshold": 0.2}
   ```

2. **Increase top_k** for more documents:
   ```json
   {"query": "your question", "top_k": 10}
   ```

3. **Check document quality** - Ensure documents are well-formatted

### No Results Returned

1. **Lower score_threshold** (try 0.1 or 0.0)
2. **Verify documents are indexed** in ChromaDB
3. **Check query relevance** - Try different phrasings

## Node.js Version Issues

### Wrong Node.js Version

If you see version errors:

**Using nvm:**
```bash
source ~/.nvm/nvm.sh
nvm use 20
# or
nvm install 20
nvm use 20
```

**Check version:**
```bash
node -v  # Should be 18+
npm -v   # Should be 9+
```

## Backend Restart

To restart the backend:

```bash
cd backend
bash reiniciar-backend.sh

# Or manually:
pkill -f uvicorn
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

## Ainda com problemas?

1. Verifique os logs: `docker compose logs -f`
2. Verifique as portas: `lsof -i -P | grep LISTEN`
3. Limpe e recomece: `docker compose down -v && docker compose up --build`
4. Verifique a documentação em `QUICKSTART.md` e `README.md`
5. Check `SECURITY.md` for security-related issues