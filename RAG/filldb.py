import json
import os
import chromadb

# setting the environment - using absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, "data")
CHROMA_PATH = os.path.join(script_dir, "chroma_db")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="federated_analysis")

# loading the JSON document

json_file_path = os.path.join(DATA_PATH, "federated.json")

# Check if the file exists
if not os.path.exists(json_file_path):
    print(f"Error: Could not find {json_file_path}")
    print(f"Current script directory: {script_dir}")
    print(f"Looking for data directory at: {DATA_PATH}")
    exit(1)

with open(json_file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Convert JSON data to text documents and prepare for ChromaDB
documents = []
metadata = []
ids = []

def create_semantic_chunks(analysis_type, result, base_id):
    """Create semantic chunks that can be matched by vector similarity"""
    chunks = []
    chunk_metadata = []
    chunk_ids = []
    
    if analysis_type == 'keyword_occurence':
        keywords = result.get('results', [])
        total_count = result.get('titleCount', 0)
        
        # Create chunks based on semantic groups rather than frequency tiers
        # Let ChromaDB's embedding model understand the semantic relationships
        
        # Chunk 1: Overview and context
        overview_chunk = f"""
Federated Learning Keyword Analysis Overview

This analysis examines keyword frequency patterns in {total_count} federated learning research papers. The analysis reveals the most commonly discussed topics, technical approaches, and application areas in federated learning research. This dataset helps understand the research landscape, trending topics, and technical focus areas within the federated learning community.

Key insights: The analysis covers a wide range of keywords from core federated learning concepts to specific technical implementations, privacy preservation methods, and application domains.
"""
        chunks.append(overview_chunk)
        chunk_ids.append(f"{base_id}_overview")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "overview",
            "total_keywords": len(keywords),
            "paper_count": total_count
        })
        
        # Chunk 2: All keywords in a searchable format
        # Create a comprehensive but natural text that includes all keywords with context
        all_keywords_chunk = f"""
Complete Keyword Frequency Analysis for Federated Learning Research

The following represents all identified keywords and their occurrence frequencies across {total_count} federated learning research papers:

"""
        for kw in keywords:
            keyword_text = kw.get('keyword', '')
            count = kw.get('count', 0)
            # Add context to make it more semantically rich
            all_keywords_chunk += f"The term '{keyword_text}' appears in {count} papers, indicating its relevance to federated learning research. "
            
        all_keywords_chunk += f"\n\nThis comprehensive keyword analysis reveals the breadth of topics covered in federated learning research, from core algorithmic concepts to practical implementation challenges and application domains."
        
        chunks.append(all_keywords_chunk)
        chunk_ids.append(f"{base_id}_complete")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "complete_keywords",
            "total_keywords": len(keywords),
            "paper_count": total_count
        })
        
    elif analysis_type == 'author_year':
        authors = result.get('results', [])
        total_count = result.get('count', 0)
        
        # Overview chunk
        overview_chunk = f"""
Federated Learning Author Publication Analysis Overview

This analysis identifies the most prolific authors in federated learning research based on publication frequency across {total_count} research papers. Understanding author productivity helps identify key researchers, research groups, and academic centers contributing to federated learning advancement.

This data reveals research leadership patterns, collaboration networks, and institutional contributions to the federated learning field.
"""
        chunks.append(overview_chunk)
        chunk_ids.append(f"{base_id}_overview")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "overview",
            "total_authors": len(authors),
            "paper_count": total_count
        })
        
        # Complete authors chunk
        all_authors_chunk = f"""
Complete Author Publication Frequency Analysis for Federated Learning Research

The following represents all authors and their publication frequencies in federated learning research:

"""
        for author in authors:
            author_name = author.get('author', '')
            count = author.get('count', 0)
            all_authors_chunk += f"Author {author_name} has published {count} papers in federated learning research, demonstrating their contribution to this field. "
            
        all_authors_chunk += f"\n\nThis author analysis helps identify research leaders, prolific contributors, and emerging researchers in the federated learning community."
        
        chunks.append(all_authors_chunk)
        chunk_ids.append(f"{base_id}_complete")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "complete_authors",
            "total_authors": len(authors),
            "paper_count": total_count
        })
        
    elif analysis_type == 'reference':
        references = result.get('results', [])
        total_count = result.get('count', 0)
        
        # Overview chunk
        overview_chunk = f"""
Federated Learning Reference Citation Analysis Overview

This analysis identifies the most frequently cited papers in federated learning research based on citation patterns across {total_count} research papers. Understanding citation patterns helps identify seminal works, influential papers, and foundational research that shapes the federated learning field.

This data reveals research impact, knowledge evolution, and fundamental contributions that define federated learning as a research area.
"""
        chunks.append(overview_chunk)
        chunk_ids.append(f"{base_id}_overview")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "overview",
            "total_references": len(references),
            "paper_count": total_count
        })
        
        # Complete references chunk
        all_references_chunk = f"""
Complete Citation Frequency Analysis for Federated Learning Research

The following represents all referenced papers and their citation frequencies in federated learning research:

"""
        for ref in references:
            title = ref.get('title', '')
            authors = ref.get('author', [])
            count = ref.get('count', 0)
            author_str = ', '.join(authors) if authors else 'Unknown authors'
            all_references_chunk += f'The paper titled "{title}" by {author_str} has been cited {count} times in federated learning research, indicating its impact on the field. '
            
        all_references_chunk += f"\n\nThis reference analysis reveals the most influential papers that have shaped federated learning research and continue to guide new developments in the field."
        
        chunks.append(all_references_chunk)
        chunk_ids.append(f"{base_id}_complete")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "complete_references",
            "total_references": len(references),
            "paper_count": total_count
        })
        
    elif analysis_type == 'field_occurence':
        fields = result.get('results', [])
        total_count = result.get('titleCount', 0)
        
        # Overview chunk
        overview_chunk = f"""
Federated Learning Research Field Distribution Analysis Overview

This analysis examines the distribution of research fields associated with federated learning publications across {total_count} research papers. Understanding field distribution helps identify interdisciplinary connections, application domains, and the cross-cutting nature of federated learning research.

This data reveals how federated learning intersects with various scientific disciplines and application areas.
"""
        chunks.append(overview_chunk)
        chunk_ids.append(f"{base_id}_overview")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "overview",
            "total_fields": len(fields),
            "paper_count": total_count
        })
        
        # Complete fields chunk
        all_fields_chunk = f"""
Complete Research Field Distribution Analysis for Federated Learning

The following represents all research fields and their occurrence frequencies in federated learning publications:

"""
        for field in fields:
            field_name = field.get('field', '')
            count = field.get('count', 0)
            all_fields_chunk += f"The research field '{field_name}' appears in {count} federated learning papers, showing the interdisciplinary nature of this research area. "
            
        all_fields_chunk += f"\n\nThis field distribution analysis demonstrates the broad applicability and interdisciplinary nature of federated learning research across multiple scientific domains."
        
        chunks.append(all_fields_chunk)
        chunk_ids.append(f"{base_id}_complete")
        chunk_metadata.append({
            "analysis_type": analysis_type,
            "chunk_type": "complete_fields",
            "total_fields": len(fields),
            "paper_count": total_count
        })
    
    return chunks, chunk_ids, chunk_metadata

# Process each analysis item
for i, item in enumerate(json_data):
    analysis_type = item.get('analysis_type', 'unknown')
    result = item.get('result', {})
    base_id = f"analysis_{analysis_type}_{i}"
    
    # Create semantic chunks for this analysis
    chunks, chunk_ids, chunk_metadata = create_semantic_chunks(analysis_type, result, base_id)
    
    # Add chunks to main lists
    documents.extend(chunks)
    ids.extend(chunk_ids)
    
    # Enrich metadata with common fields
    for meta_item in chunk_metadata:
        meta_item.update({
            "source": "federated.json",
            "doc_id": i,
            "workspace_id": item.get('workspace_id', 'unknown'),
            "result_type": result.get('type', 'unknown'),
            "created_at": item.get('created_at', {}).get('$date', 'unknown')
        })
    
    metadata.extend(chunk_metadata)

print(f"Prepared {len(documents)} document chunks for insertion into ChromaDB")

# adding to chromadb


collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)