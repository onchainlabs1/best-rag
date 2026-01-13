#!/usr/bin/env python3
"""Script para testar se o retrieval está funcionando."""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.shared_services import document_service, agent_service
    from src.schemas.api import QueryRequest
    
    print("✅ Imports OK")
    
    # Verificar quantos documentos há no ChromaDB
    try:
        count = agent_service.retriever.collection.count()
        print(f"✅ ChromaDB Collection: {count} documentos")
    except Exception as e:
        print(f"❌ Erro ao contar documentos: {e}")
    
    # Testar uma busca simples
    if count > 0:
        print("\n🔍 Testando busca...")
        result = agent_service.retriever.retrieve(
            "teste",
            top_k=5,
            score_threshold=0.1  # Threshold muito baixo para pegar qualquer coisa
        )
        print(f"✅ Busca retornou: {len(result.chunks)} chunks")
        if result.chunks:
            for i, (chunk, score) in enumerate(zip(result.chunks[:3], result.scores[:3])):
                print(f"  {i+1}. Score: {score:.3f} - {chunk.content[:60]}...")
        else:
            print("  ⚠️  Nenhum chunk encontrado mesmo com threshold baixo")
    else:
        print("⚠️  Nenhum documento no ChromaDB. Faça upload primeiro.")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
