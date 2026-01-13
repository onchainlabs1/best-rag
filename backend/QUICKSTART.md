# Quick Start - Backend Local

## Setup em 3 Passos

### 1. Instalar Dependências

```bash
cd backend
./scripts/setup.sh
```

**Nota**: Se o Poetry não funcionar, o script tentará usar `pip` diretamente.

### 2. Iniciar Servidor

```bash
./scripts/start-backend.sh
```

### 3. Acessar API

Abra no navegador: http://localhost:8080/docs

## Verificar Status

```bash
./scripts/check-status.sh
```

## Comandos Manuais (Alternativa)

Se os scripts não funcionarem:

```bash
# 1. Criar venv
python3 -m venv .venv

# 2. Ativar venv
source .venv/bin/activate

# 3. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# 4. Criar diretórios
mkdir -p data/chroma

# 5. Copiar .env (se não existir)
cp .env.example .env  # ou criar manualmente

# 6. Iniciar servidor
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

## Troubleshooting

- **Erro de permissão**: Execute `chmod +x scripts/*.sh`
- **Porta ocupada**: Altere a porta no comando (ex: `--port 8081`)
- **Módulo não encontrado**: Execute `pip install -r requirements.txt` novamente

## Próximos Passos

1. Teste o endpoint de health: http://localhost:8080/api/v1/health
2. Faça upload de um documento via Swagger UI
3. Teste uma query
