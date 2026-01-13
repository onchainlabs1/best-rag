# Frontend - RAG + Agent Knowledge Base

Frontend Next.js 15 com TypeScript e Tailwind CSS.

## Pré-requisitos

- Node.js 18+ 
- npm 9+

## Instalação

```bash
cd frontend
npm install
```

## Executar Localmente

### Opção 1: Usando o script

```bash
# Na raiz do projeto
./scripts/start-frontend.sh
```

### Opção 2: Manualmente

```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:3000` (ou porta configurada).

## Configuração de Porta

Para usar uma porta diferente (ex: 3001):

```bash
# Via variável de ambiente
FRONTEND_PORT=3001 npm run dev

# Ou via script
FRONTEND_PORT=3001 ./scripts/start-frontend.sh
```

## Configuração da API

A URL da API pode ser configurada via variável de ambiente:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

Ou criar um arquivo `.env.local` no diretório `frontend/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Scripts Disponíveis

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Build para produção
- `npm run start` - Inicia servidor de produção
- `npm run lint` - Executa linter
- `npm run type-check` - Verifica tipos TypeScript

## Estrutura

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Layout principal
│   │   ├── page.tsx      # Página inicial
│   │   └── globals.css   # Estilos globais
│   ├── components/       # Componentes React
│   │   ├── DocumentUpload.tsx
│   │   └── QueryInterface.tsx
│   ├── lib/             # Utilitários
│   └── types/           # Tipos TypeScript
├── public/              # Arquivos estáticos
├── package.json
├── tsconfig.json
└── next.config.js
```

## Troubleshooting

### Porta já em uso

```bash
# Verificar porta em uso
lsof -i :3000

# Usar outra porta
npm run dev -- -p 3001
```

### Erro de dependências

```bash
rm -rf node_modules package-lock.json
npm install
```

### Erro de TypeScript

```bash
npm run type-check
```
