# Rodar Backend Localmente

Este guia explica como rodar o backend do projeto RAG + Agent Knowledge Base localmente.

## Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes Python)

## Setup Rápido

### 1. Instalar Dependências

```bash
cd backend
./scripts/setup.sh
```

Este script irá:
- Criar ambiente virtual (`.venv`)
- Instalar todas as dependências
- Criar diretórios necessários
- Copiar `.env.example` para `.env` se não existir

### 2. Configurar Variáveis de Ambiente

O arquivo `.env` já está configurado para modo simplificado:
- **Embeddings**: Usa modelo local (`all-MiniLM-L6-v2`) - não precisa API key
- **ChromaDB**: Usa caminho local (`./data/chroma`)
- **LLM**: Configurado para `local` (pode precisar ajustar depois)

Se quiser usar OpenAI para LLM, edite `.env` e adicione:
```bash
OPENAI_API_KEY=your_key_here
LLM_PROVIDER=openai
```

### 3. Iniciar Servidor

```bash
./scripts/start-backend.sh
```

Ou manualmente:
```bash
source .venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Verificar Status

```bash
./scripts/check-status.sh
```

## Acessar API

Após iniciar o servidor:

- **API Docs (Swagger)**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/api/v1/health

## Estrutura de Diretórios

```
backend/
├── src/              # Código fonte
├── tests/           # Testes
├── scripts/         # Scripts de setup/start
├── data/            # Dados locais (ChromaDB)
│   └── chroma/      # Banco vetorial
├── .venv/           # Ambiente virtual (criado pelo setup)
├── .env             # Variáveis de ambiente (criado pelo setup)
└── requirements.txt # Dependências Python
```

## Modo Simplificado

O projeto está configurado para rodar em **modo simplificado**:

- ✅ **Sem PostgreSQL**: DocumentService usa dict em memória
- ✅ **Embeddings Locais**: Usa `sentence-transformers` (não precisa API key)
- ✅ **ChromaDB Local**: Persistência local em `./data/chroma`
- ⚠️ **LLM**: Por enquanto ainda usa OpenAI (pode ser configurado depois)

## Troubleshooting

### Erro: "ModuleNotFoundError"

Execute novamente:
```bash
source .venv/bin/activate
pip install -r requirements.txt --no-cache-dir
```

### Erro: "Permission denied"

Certifique-se de que os scripts são executáveis:
```bash
chmod +x scripts/*.sh
```

### Erro: "ChromaDB path not found"

Crie o diretório manualmente:
```bash
mkdir -p data/chroma
```

### Porta 8080 já em uso

Altere a porta no script `start-backend.sh` ou use:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8081 --reload
```

## Próximos Passos

1. Testar upload de documentos: `POST /api/v1/documents/upload`
2. Testar queries: `POST /api/v1/queries`
3. Verificar logs no terminal

## Comandos Úteis

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Rodar testes
pytest

# Verificar tipos
mypy src/

# Formatar código
ruff format src/

# Verificar lint
ruff check src/
```
