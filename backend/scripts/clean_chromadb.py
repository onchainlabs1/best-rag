#!/usr/bin/env python3
"""Script to clean ChromaDB and remove corrupted base64 content."""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from src.rag.retriever import RAGRetriever
from src.config import Settings
import structlog

logger = structlog.get_logger()


def clean_chromadb():
    """Remove all documents from ChromaDB."""
    try:
        settings = Settings()
        retriever = RAGRetriever(settings)
        
        # Get collection count
        count = retriever.collection.count()
        print(f"📊 Found {count} chunks in ChromaDB")
        
        if count == 0:
            print("✅ ChromaDB is already empty")
            return
        
        # Get all IDs
        print("🔍 Retrieving all chunk IDs...")
        results = retriever.collection.get(include=["metadatas", "ids", "documents"])
        
        if results and results.get("ids"):
            chunk_ids = results["ids"]
            print(f"🗑️  Deleting {len(chunk_ids)} chunks...")
            
            # Delete all chunks
            retriever.collection.delete(ids=chunk_ids)
            
            # Verify deletion
            new_count = retriever.collection.count()
            print(f"✅ ChromaDB cleaned! Remaining chunks: {new_count}")
            
            if new_count == 0:
                print("✅ Successfully removed all corrupted content")
            else:
                print(f"⚠️  Warning: {new_count} chunks remain")
        else:
            print("⚠️  No chunks found to delete")
            
    except Exception as e:
        print(f"❌ Error cleaning ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("🧹 Cleaning ChromaDB...")
    print("=" * 50)
    clean_chromadb()
    print("=" * 50)
    print("✅ Done! You can now upload documents again.")
