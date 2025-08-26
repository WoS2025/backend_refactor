#!/usr/bin/env python3
"""
Complete LLM Data Ingestion Script
This script will ingest the LLM data into ChromaDB
"""

import json
import os
import chromadb
import sys

def main():
    print("🚀 Starting LLM data ingestion...")
    
    # Set up paths
    base_dir = "/Users/aaronwu/Documents/GitHub/connect refactor and fe/backend_refactor"
    rag_dir = os.path.join(base_dir, "RAG")
    data_path = os.path.join(rag_dir, "data")
    chroma_path = os.path.join(rag_dir, "chroma_db")
    json_file_path = os.path.join(data_path, "llm.json")
    
    print(f"📁 RAG directory: {rag_dir}")
    print(f"📄 Data path: {data_path}")
    print(f"🗄️ ChromaDB path: {chroma_path}")
    print(f"📋 JSON file: {json_file_path}")
    
    # Check if JSON file exists
    if not os.path.exists(json_file_path):
        print(f"❌ Error: Could not find {json_file_path}")
        return False
    
    print(f"✅ Found JSON file")
    
    # Initialize ChromaDB
    try:
        chroma_client = chromadb.PersistentClient(path=chroma_path)
        collection = chroma_client.get_or_create_collection(name="llm_analysis")
        print(f"✅ Connected to collection: llm_analysis")
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False
    
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        print(f"📊 Loaded {len(json_data)} items from JSON file")
    except Exception as e:
        print(f"❌ JSON loading error: {e}")
        return False
    
    # Process data
    documents = []
    metadata = []
    ids = []
    
    print("🔄 Processing data items...")
    
    for i, item in enumerate(json_data):
        analysis_type = item.get('analysis_type', 'unknown')
        result = item.get('result', {})
        
        # Create searchable content based on analysis type
        if analysis_type == 'keyword_occurence':
            keywords = result.get('results', [])
            top_keywords = keywords[:20]
            
            text_content = f"""
Analysis Type: Keyword Analysis
This contains the top keywords found in large language model (LLM) research.
Top Keywords by Frequency:
"""
            for idx, kw in enumerate(top_keywords, 1):
                text_content += f"{idx}. {kw.get('keyword', '')}: {kw.get('count', 0)} occurrences\n"
            
            text_content += f"\nTotal title count: {result.get('titleCount', 0)}\n"
            text_content += f"Analysis covers keyword frequency analysis of large language model research papers.\n"
            
        elif analysis_type == 'author_year':
            authors = result.get('results', [])
            top_authors = authors[:20]
            
            text_content = f"""
Analysis Type: Author Analysis
This contains the top authors in large language model (LLM) research.
Top Authors by Publication Count:
"""
            for idx, author in enumerate(top_authors, 1):
                text_content += f"{idx}. {author.get('author', '')}: {author.get('count', 0)} publications\n"
            
            text_content += f"\nTotal authors analyzed: {result.get('count', 0)}\n"
            text_content += f"Analysis covers author publication frequency in large language model research.\n"
            
        elif analysis_type == 'reference':
            references = result.get('results', [])
            top_references = references[:20]
            
            text_content = f"""
Analysis Type: Reference Analysis
This contains the most cited papers in large language model (LLM) research.
Top Referenced Papers by Citation Count:
"""
            for idx, ref in enumerate(top_references, 1):
                title = ref.get('title', '')
                authors = ref.get('author', [])
                count = ref.get('count', 0)
                author_str = ', '.join(authors) if authors else 'Unknown'
                text_content += f"{idx}. \"{title}\" by {author_str}: {count} citations\n"
            
            text_content += f"\nTotal papers analyzed: {result.get('count', 0)}\n"
            text_content += f"Analysis covers citation frequency of large language model research papers.\n"
            
        elif analysis_type == 'field_occurence':
            fields = result.get('results', [])
            top_fields = fields[:20]
            
            text_content = f"""
Analysis Type: Field Analysis
This contains the top research fields in large language model (LLM) research.
Top Research Fields by Frequency:
"""
            for idx, field in enumerate(top_fields, 1):
                text_content += f"{idx}. {field.get('field', '')}: {field.get('count', 0)} occurrences\n"
            
            text_content += f"\nTotal titles analyzed: {result.get('titleCount', 0)}\n"
            text_content += f"Analysis covers research field classification of large language model papers.\n"
            
        else:
            text_content = f"""
Analysis Type: {analysis_type}
Workspace ID: {item.get('workspace_id', 'N/A')}
Result: {json.dumps(result, indent=2)}
"""
        
        documents.append(text_content)
        ids.append(f"analysis_{analysis_type}_{i}")
        metadata.append({
            "source": "llm.json",
            "doc_id": i,
            "analysis_type": analysis_type,
            "workspace_id": item.get('workspace_id', 'unknown'),
            "result_type": result.get('type', 'unknown'),
            "total_count": result.get('count', 0) or result.get('titleCount', 0)
        })
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1} items...")
    
    print(f"📝 Prepared {len(documents)} document chunks")
    
    # Insert into ChromaDB
    try:
        print("💾 Inserting documents into ChromaDB...")
        collection.upsert(
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        
        final_count = collection.count()
        print(f"✅ Successfully inserted {len(documents)} documents!")
        print(f"🗃️ Collection now contains {final_count} total documents")
        print("🎉 LLM data ingestion completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Insertion error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to test! You can now:")
        print("  1. Run 'python3 RAG/ask.py' for CLI chat")
        print("  2. Start your Flask app to test API endpoints") 
        print("  3. Test with: 'What are the top LLM keywords?'")
    else:
        print("\n❌ Ingestion failed. Check the errors above.")
        sys.exit(1)
