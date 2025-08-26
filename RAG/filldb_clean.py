#!/usr/bin/env python3
"""
Fill ChromaDB with LLM research data for RAG system
"""
import chromadb
import json
import os

def main():
    print("🚀 Starting ChromaDB population with clean LLM data...")
    
    # Initialize ChromaDB client with explicit path
    import os
    db_path = 'RAG/chroma_db'
    print(f"📁 Using ChromaDB path: {os.path.abspath(db_path)}")
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or get collection for clean LLM analysis
    collection_name = "llm_analysis_clean"
    try:
        collection = client.delete_collection(collection_name)
        print(f"🗑️  Deleted existing collection: {collection_name}")
    except:
        pass
    
    collection = client.create_collection(collection_name)
    print(f"✅ Created collection: {collection_name}")

    # Load the clean LLM research data
    with open('RAG/data/llm_clean.json', 'r') as f:
        data = json.load(f)
    
    print(f"📊 Loaded {len(data)} items from clean JSON file")

    # Convert clean data to text documents
    documents = []
    metadata = []
    ids = []

    print("🔄 Processing clean data items...")

    for i, item in enumerate(data):
        analysis_type = item.get('analysis_type', 'unknown')
        
        # Create searchable content based on analysis type
        if analysis_type == 'keyword_analysis':
            title = item.get('title', 'Keyword Analysis')
            description = item.get('description', '')
            keywords = item.get('top_keywords', [])
            
            content = f"""
Analysis Type: {title}
{description}
Top Keywords:
"""
            for j, keyword in enumerate(keywords[:20], 1):
                kw_name = keyword.get('keyword', '')
                kw_count = keyword.get('count', 0)
                content += f"{j}. \"{kw_name}\": {kw_count} occurrences\n"
            
            documents.append(content.strip())
            metadata.append({
                "analysis_type": analysis_type,
                "source": "keyword_analysis"
            })
            ids.append(f"analysis_{analysis_type}_{i}")

        elif analysis_type == 'author_analysis':
            title = item.get('title', 'Author Analysis') 
            description = item.get('description', '')
            authors = item.get('top_authors', [])
            
            content = f"""
Analysis Type: {title}
{description}
Top Authors by Publication Count:
"""
            for j, author in enumerate(authors[:50], 1):
                author_name = author.get('name', '') or author.get('authorName', '')
                pub_count = author.get('publicationCount', 0)
                content += f"{j}. {author_name}: {pub_count} publications\n"
            
            documents.append(content.strip())
            metadata.append({
                "analysis_type": analysis_type,
                "source": "author_analysis"
            })
            ids.append(f"analysis_{analysis_type}_{i}")

        elif analysis_type == 'field_analysis':
            title = item.get('title', 'Field Analysis')
            description = item.get('description', '')
            fields = item.get('top_fields', [])
            
            content = f"""
Analysis Type: {title}
{description}
Top Research Fields:
"""
            for j, field in enumerate(fields[:30], 1):
                field_name = field.get('field', '') or field.get('name', '')
                field_count = field.get('count', 0)
                content += f"{j}. {field_name}: {field_count} papers\n"
            
            documents.append(content.strip())
            metadata.append({
                "analysis_type": analysis_type,
                "source": "field_analysis"
            })
            ids.append(f"analysis_{analysis_type}_{i}")

        elif analysis_type == 'paper_citation':
            title = item.get('paper_title', 'Unknown Paper')
            authors = item.get('authors', 'Unknown Authors')
            citations = item.get('citation_count', 0)
            searchable = item.get('searchable_text', '')
            
            content = f"""
Paper Title: {title}
Authors: {authors}
Citations: {citations}
Type: Research paper in LLM database
Searchable: {searchable}
"""
            
            documents.append(content.strip())
            metadata.append({
                "analysis_type": analysis_type,
                "paper_title": title,
                "authors": authors,
                "citations": citations
            })
            ids.append(f"paper_{i}")

    print(f"📄 Created {len(documents)} searchable documents")

    # Add documents to ChromaDB in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metadata = metadata[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metadata,
            ids=batch_ids
        )
        print(f"✅ Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

    # Verify the data
    total_count = collection.count()
    print(f"🎯 Successfully added {total_count} documents to ChromaDB")
    
    # Test query
    results = collection.query(
        query_texts=["cognitive training"],
        n_results=3
    )
    
    print(f"🔍 Test query 'cognitive training' found {len(results['documents'][0])} results")
    if results['documents'][0]:
        first_result = results['documents'][0][0]
        print(f"📝 First result: {first_result[:200]}...")

if __name__ == "__main__":
    main()
