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

for i, item in enumerate(json_data):
    analysis_type = item.get('analysis_type', 'unknown')
    result = item.get('result', {})
    
    # Create more searchable content based on analysis type
    if analysis_type == 'keyword_occurence':
        # Create keyword-focused content
        keywords = result.get('results', [])
        top_keywords = keywords[:20]  # Get top 20 keywords
        
        text_content = f"""
Analysis Type: Keyword Analysis
This contains the top keywords found in federated learning research.
Top Keywords by Frequency:
"""
        for idx, kw in enumerate(top_keywords, 1):
            text_content += f"{idx}. {kw.get('keyword', '')}: {kw.get('count', 0)} occurrences\n"
        
        text_content += f"\nTotal title count: {result.get('titleCount', 0)}\n"
        text_content += f"Analysis covers keyword frequency analysis of federated learning research papers.\n"
        
    elif analysis_type == 'author_year':
        # Create author-focused content
        authors = result.get('results', [])
        top_authors = authors[:20]  # Get top 20 authors
        
        text_content = f"""
Analysis Type: Author Analysis
This contains the top authors in federated learning research.
Top Authors by Publication Count:
"""
        for idx, author in enumerate(top_authors, 1):
            text_content += f"{idx}. {author.get('author', '')}: {author.get('count', 0)} publications\n"
        
        text_content += f"\nTotal authors analyzed: {result.get('count', 0)}\n"
        text_content += f"Analysis covers author publication frequency in federated learning research.\n"
        
    elif analysis_type == 'reference':
        # Create reference-focused content
        references = result.get('results', [])
        top_references = references[:20]  # Get top 20 references
        
        text_content = f"""
Analysis Type: Reference Analysis
This contains the most cited papers in federated learning research.
Top Referenced Papers by Citation Count:
"""
        for idx, ref in enumerate(top_references, 1):
            title = ref.get('title', '')
            authors = ref.get('author', [])
            count = ref.get('count', 0)
            author_str = ', '.join(authors) if authors else 'Unknown'
            text_content += f"{idx}. \"{title}\" by {author_str}: {count} citations\n"
        
        text_content += f"\nTotal papers analyzed: {result.get('count', 0)}\n"
        text_content += f"Analysis covers citation frequency of federated learning research papers.\n"
        
    elif analysis_type == 'field_occurence':
        # Create field-focused content
        fields = result.get('results', [])
        top_fields = fields[:20]  # Get top 20 fields
        
        text_content = f"""
Analysis Type: Field Analysis
This contains the top research fields in federated learning.
Top Research Fields by Frequency:
"""
        for idx, field in enumerate(top_fields, 1):
            text_content += f"{idx}. {field.get('field', '')}: {field.get('count', 0)} occurrences\n"
        
        text_content += f"\nTotal titles analyzed: {result.get('titleCount', 0)}\n"
        text_content += f"Analysis covers research field classification of federated learning papers.\n"
        
    else:
        # Fallback for unknown analysis types
        text_content = f"""
Analysis Type: {analysis_type}
Workspace ID: {item.get('workspace_id', 'N/A')}
Result: {json.dumps(result, indent=2)}
"""
    
    # Don't chunk this data - keep each analysis as a single document
    documents.append(text_content)
    ids.append(f"analysis_{analysis_type}_{i}")
    metadata.append({
        "source": "federated.json",
        "doc_id": i,
        "analysis_type": analysis_type,
        "workspace_id": item.get('workspace_id', 'unknown'),
        "result_type": result.get('type', 'unknown'),
        "total_count": result.get('count', 0) or result.get('titleCount', 0)
    })

print(f"Prepared {len(documents)} document chunks for insertion into ChromaDB")

# adding to chromadb


collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)