# Solução para Erro npm install

## Erro Encontrado

```
npm ERR! code EINVALIDTAGNAME
npm ERR! Invalid tag name "#" of package "#"
```

## Solução

Execute estes comandos na ordem:

### 1. Ativar Node.js 20

```bash
source ~/.nvm/nvm.sh
nvm use 20
```

### 2. Limpar cache do npm

```bash
npm cache clean --force
```

### 3. Remover node_modules e package-lock.json (se existir)

```bash
cd frontend
rm -rf node_modules package-lock.json
```

### 4. Reinstalar dependências

```bash
npm install
```

### 5. Se ainda der erro, tente com yarn

```bash
# Instalar yarn se não tiver
npm install -g yarn

# Usar yarn ao invés de npm
yarn install
```

## Comando Completo

```bash
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Alternativa: Usar Yarn

Se npm continuar dando problema:

```bash
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
yarn install
PORT=3001 yarn dev
```
