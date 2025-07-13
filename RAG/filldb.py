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
    # Convert each JSON object to a readable text format
    text_content = f"""
Analysis Type: {item.get('analysis_type', 'N/A')}
Workspace ID: {item.get('workspace_id', 'N/A')}
Result: {json.dumps(item.get('result', {}), indent=2)}
"""
    
    # Split long content into smaller chunks if needed
    max_chunk_size = 1000
    if len(text_content) > max_chunk_size:
        # Simple splitting by characters
        chunks = [text_content[i:i+max_chunk_size] for i in range(0, len(text_content), max_chunk_size-100)]
        for j, chunk in enumerate(chunks):
            documents.append(chunk)
            ids.append(f"doc_{i}_chunk_{j}")
            metadata.append({
                "source": "federated.json",
                "original_doc_id": i,
                "chunk_id": j,
                "analysis_type": item.get('analysis_type', 'unknown'),
                "workspace_id": item.get('workspace_id', 'unknown')
            })
    else:
        documents.append(text_content)
        ids.append(f"doc_{i}")
        metadata.append({
            "source": "federated.json",
            "doc_id": i,
            "analysis_type": item.get('analysis_type', 'unknown'),
            "workspace_id": item.get('workspace_id', 'unknown')
        })

print(f"Prepared {len(documents)} document chunks for insertion into ChromaDB")

# adding to chromadb


collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)