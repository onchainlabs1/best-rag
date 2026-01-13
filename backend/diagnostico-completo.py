#!/usr/bin/env python3
"""Script completo de diagnóstico do sistema."""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA")
print("=" * 60)

try:
    print("\n1️⃣ Verificando imports...")
    from src.shared_services import document_service, agent_service
    from src.rag.retriever import RAGRetriever
    from src.schemas.api import QueryRequest
    print("✅ Imports OK")
    
    print("\n2️⃣ Verificando ChromaDB...")
    retriever = agent_service.retriever
    print(f"   Collection name: {retriever.collection_name}")
    print(f"   ChromaDB path: {retriever.client._settings.path}")
    
    try:
        count = retriever.collection.count()
        print(f"   ✅ Total de documentos no ChromaDB: {count}")
    except Exception as e:
        print(f"   ❌ Erro ao contar: {e}")
        count = 0
    
    if count == 0:
        print("\n⚠️  PROBLEMA ENCONTRADO: ChromaDB está vazio!")
        print("   Isso significa que os documentos não foram salvos.")
        print("   Possíveis causas:")
        print("   - Erro durante o upload")
        print("   - Erro ao gerar embeddings")
        print("   - Erro ao salvar no ChromaDB")
        print("\n   Verifique os logs do backend durante o upload.")
    else:
        print(f"\n3️⃣ Testando busca com {count} documentos...")
        
        # Testar várias queries
        test_queries = [
            "teste",
            "documento",
            "conteúdo",
            "informação"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                result = retriever.retrieve(
                    query=query,
                    top_k=5,
                    score_threshold=0.0  # Sem threshold para pegar tudo
                )
                print(f"   ✅ Encontrou {len(result.chunks)} chunks")
                if result.chunks:
                    print(f"   Scores: {[f'{s:.3f}' for s in result.scores[:3]]}")
                    print(f"   Primeiro chunk: {result.chunks[0].content[:80]}...")
                else:
                    print("   ⚠️  Nenhum chunk encontrado mesmo sem threshold!")
            except Exception as e:
                print(f"   ❌ Erro na busca: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n4️⃣ Verificando documentos no DocumentService...")
        docs = document_service.list_documents()
        print(f"   Documentos em memória: {len(docs)}")
        for doc in docs:
            print(f"   - {doc.filename} (ID: {doc.id}, Chunks: {doc.chunk_count})")
        
        if len(docs) > 0 and count == 0:
            print("\n⚠️  PROBLEMA: DocumentService tem documentos mas ChromaDB está vazio!")
            print("   Isso significa que o upload foi registrado mas não foi salvo no ChromaDB.")
        
        if len(docs) == 0 and count > 0:
            print("\n⚠️  PROBLEMA: ChromaDB tem documentos mas DocumentService não!")
            print("   Isso significa que os dados estão no ChromaDB mas não em memória.")
            print("   Isso é OK se você reiniciou o backend - DocumentService é em memória.")
        
        if len(docs) > 0 and count > 0:
            print("\n✅ Tudo parece estar OK! O problema pode ser:")
            print("   - Query muito específica")
            print("   - Embeddings não estão funcionando bem")
            print("   - Threshold muito alto (mas já testamos com 0.0)")
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completo!")
    print("=" * 60)
        
except Exception as e:
    print(f"\n❌ Erro durante diagnóstico: {e}")
    import traceback
    traceback.print_exc()
