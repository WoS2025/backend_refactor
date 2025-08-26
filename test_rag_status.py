import sys
import os
sys.path.append('/Users/aaronwu/Documents/GitHub/connect refactor and fe/backend_refactor')

try:
    from service.rag_service import RAGService
    print("✅ RAGService imported successfully")
    
    rag = RAGService()
    print("✅ RAGService initialized")
    
    stats = rag.get_collection_stats()
    print(f"📊 Collection stats: {stats}")
    
    if stats.get('success') and stats.get('total_documents', 0) > 0:
        print("🎉 RAG system is working with data!")
        
        # Test a search
        result = rag.search_documents("large language models", 1)
        if result.get('success'):
            print(f"🔍 Search test successful: found {result.get('total_found', 0)} documents")
            if result.get('documents'):
                print(f"📄 Sample content: {result['documents'][0]['content'][:100]}...")
        else:
            print(f"❌ Search test failed: {result}")
    else:
        print("⚠️ RAG system has no data or connection issues")
        print("Need to run filldb.py")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("❌ RAG system not working properly")
