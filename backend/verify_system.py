#!/usr/bin/env python3
"""System verification script to ensure everything is working."""

import sys
import json
from typing import Dict, Any

def check_backend_health() -> Dict[str, Any]:
    """Check if backend is healthy."""
    try:
        import requests
        response = requests.get("http://localhost:8080/api/v1/health", timeout=5)
        if response.status_code == 200:
            return {"status": "ok", "data": response.json()}
        return {"status": "error", "message": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_documents_indexed() -> Dict[str, Any]:
    """Check if documents are indexed."""
    try:
        from src.shared_services import agent_service
        count = agent_service.retriever.collection.count()
        return {"status": "ok", "count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def test_agent_query() -> Dict[str, Any]:
    """Test agent query processing."""
    try:
        from src.shared_services import agent_service
        from src.schemas.api import QueryRequest
        
        request = QueryRequest(
            query="What is this document about?",
            top_k=3,
            score_threshold=0.3,
            stream=False
        )
        
        response = agent_service.process_query(request)
        
        return {
            "status": "ok",
            "has_answer": bool(response.answer),
            "answer_length": len(response.answer),
            "sources_count": len(response.sources),
            "validation_score": response.score,
            "iteration_count": response.metadata.get("iteration_count", 0),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Run all checks."""
    print("🔍 Verifying System Status...\n")
    
    results = {}
    
    # Check backend health
    print("1. Checking backend health...")
    health = check_backend_health()
    results["backend_health"] = health
    if health["status"] == "ok":
        print(f"   ✅ Backend is healthy (version: {health['data'].get('version', 'unknown')})")
    else:
        print(f"   ❌ Backend health check failed: {health['message']}")
        print("   ⚠️  Make sure backend is running on port 8080")
    
    # Check documents
    print("\n2. Checking indexed documents...")
    docs = check_documents_indexed()
    results["documents"] = docs
    if docs["status"] == "ok":
        print(f"   ✅ Found {docs['count']} indexed documents")
        if docs["count"] == 0:
            print("   ⚠️  No documents indexed. Upload documents first.")
    else:
        print(f"   ❌ Failed to check documents: {docs['message']}")
    
    # Test agent
    print("\n3. Testing agent workflow...")
    agent_test = test_agent_query()
    results["agent"] = agent_test
    if agent_test["status"] == "ok":
        print(f"   ✅ Agent is working")
        print(f"   - Answer generated: {agent_test['has_answer']}")
        print(f"   - Answer length: {agent_test['answer_length']} chars")
        print(f"   - Sources found: {agent_test['sources_count']}")
        print(f"   - Validation score: {agent_test['validation_score']:.2f}")
        print(f"   - Iterations: {agent_test['iteration_count']}")
    else:
        print(f"   ❌ Agent test failed: {agent_test['message']}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 Summary:")
    print("="*50)
    
    all_ok = (
        health["status"] == "ok" and
        docs["status"] == "ok" and
        agent_test["status"] == "ok"
    )
    
    if all_ok:
        print("✅ All systems operational!")
        if docs.get("count", 0) > 0:
            print("✅ System is ready to use")
        else:
            print("⚠️  System is ready but no documents indexed yet")
        return 0
    else:
        print("❌ Some checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
