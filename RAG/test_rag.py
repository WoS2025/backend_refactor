#!/usr/bin/env python3

import chromadb
import json
import os

# Test the RAG system without OpenAI
script_dir = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(script_dir, "chroma_db")

print("Testing ChromaDB connection...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="federated_analysis")

print(f"Collection has {collection.count()} documents")

# Test search
test_queries = [
    "federated learning",
    "keywords analysis", 
    "training data",
    "privacy"
]

for query in test_queries:
    print(f"\n--- Testing query: '{query}' ---")
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    
    if results['documents'][0]:
        print(f"Found {len(results['documents'][0])} relevant documents")
        for i, doc in enumerate(results['documents'][0]):
            print(f"\nDocument {i+1} (distance: {results['distances'][0][i]:.3f}):")
            print(doc[:300] + "..." if len(doc) > 300 else doc)
            print(f"Metadata: {results['metadatas'][0][i]}")
    else:
        print("No documents found")

print("\n=== RAG Database Test Complete ===")
