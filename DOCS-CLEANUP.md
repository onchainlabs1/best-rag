# Documentation Cleanup Plan

## Files to Keep (Core Documentation)

### Root Level
- `README.md` - Main project readme ✅
- `ARCHITECTURE.md` - System architecture ✅
- `LICENSE` - License file ✅
- `CONTRIBUTING.md` - Contribution guidelines ✅
- `API.md` - API documentation ✅
- `SECURITY.md` - Security considerations ✅
- `QUICKSTART.md` - Quick start guide ✅
- `TROUBLESHOOTING.md` - Common issues ✅

### Review/Status Files (Keep for Reference)
- `DEEP-REVIEW.md` - Code review
- `CODEX-FIXES.md` - Fixes applied
- `CODEX-FINAL-FIXES.md` - Final fixes
- `SYSTEM-VERIFIED.md` - System verification

## Files to Remove (Redundant/Temporary)

### Redundant Quick Start Guides
- `COMANDO-FINAL.md`
- `COMANDO-RAPIDO.md`
- `EXECUTAR-AGORA.md`
- `EXECUTE-ESTES-COMANDOS.md`
- `START-NOW.md`
- `INSTALAR-E-RODAR.md`
- `LEIA-ISSO.md`

### Redundant Frontend Guides
- `COMO-INICIAR-FRONTEND.md`
- `INICIAR-FRONTEND-AGORA.md`
- `INICIAR-FRONTEND-CORRETO.md`
- `FRONTEND-RODANDO.md`
- `RUN-FRONTEND.md`
- `LINK-DO-SITE.md`

### Redundant Backend Guides
- `REINICIAR-BACKEND.md`
- `VERIFICAR-ERROS.md`
- `SOLUCAO-ERRO.md`
- `SOLUCAO-RAPIDA.md`
- `USAR-NODE-20.md`

### Redundant Setup Guides
- `COMO-RODAR.md` (consolidate into QUICKSTART.md)
- `COMO-USAR-INTERFACE.md` (consolidate into README.md)

### Backend-Specific Troubleshooting (Move to TROUBLESHOOTING.md)
- `backend/RE-UPLOAD-NECESSARIO.md`
- `backend/MELHORIAS-RESPOSTAS.md`
- `backend/STATUS-DOCLING.md`
- `backend/DOCLING-CORRIGIDO.md`
- `backend/DOCLING-INTEGRADO.md`
- `backend/INTEGRACAO-COMPLETA.md`
- `backend/MODELO-ATUALIZADO.md`
- `backend/CONFIGURADO-GROQ.md`
- `backend/CONFIGURAR-OPENAI.md`
- `backend/MELHORIAS-QUALIDADE.md`
- `backend/MELHORIAS-APLICADAS.md`
- `backend/SOLUCAO-RAPIDA.md`
- `backend/VERIFICAR-DEBUG.md`
- `backend/TESTAR-FUNCIONAMENTO.md`
- `backend/DEBUG-RETRIEVAL.md`
- `backend/CORRIGIR-ERRO-BATCH.md`
- `backend/ACELERAR-PROCESSAMENTO.md`
- `backend/OTIMIZACOES-PERFORMANCE.md`

### Status/Review Files (Keep but organize)
- `TRANSLATED-TO-ENGLISH.md` - Can be removed (already done)
- `REVIEW-SUMMARY.md` - Keep for reference
- `PRE-GITHUB-CHECKLIST.md` - Keep for reference

### Scripts (Keep but organize)
- `INICIAR-TUDO.sh` - Keep
- `start-site.sh` - Keep
- Move to `scripts/` directory

## Action Plan

1. **Consolidate** redundant guides into `QUICKSTART.md`
2. **Move** backend troubleshooting to `TROUBLESHOOTING.md`
3. **Remove** temporary/redundant files
4. **Organize** scripts into `scripts/` directory
5. **Update** references in remaining docs

## Commands to Clean Up

```bash
# Remove redundant files (after consolidating content)
rm COMANDO-FINAL.md COMANDO-RAPIDO.md EXECUTAR-AGORA.md ...
```
