import chromadb
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# setting the environment - using absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, "data")
CHROMA_PATH = os.path.join(script_dir, "chroma_db")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="federated_analysis")


user_query = input("What do you want to know about federated learning analysis?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=1  # Increased from 1 to get more relevant results
)

# Uncomment below lines for debugging if needed
# print("DEBUG: Search results:")
# print("Documents found:", len(results['documents'][0]))
# print("Sample document:", results['documents'][0][0][:200] if results['documents'][0] else "No documents found")
# print("Metadata:", results['metadatas'][0][0] if results['metadatas'][0] else "No metadata")
# print("Distance scores:", results['distances'][0] if 'distances' in results else "No distances")

#print(results['documents'])
#print(results['metadatas'])

client = OpenAI()

# Check if we have data
if not results['documents'][0]:
    print("No relevant documents found in the database.")
    exit(1)

system_prompt = """
You are a helpful assistant. You answer questions about federated learning analysis and research data.
But you only answer based on knowledge I'm providing you. You don't use your internal 
knowledge and you don't make things up.

If you don't know the answer, just say: I don't know

--------------------

The data:

"""+str(results['documents'])+"""

"""

#print(system_prompt)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_query}    
        ]
    )
    
    print("\n\n---------------------\n\n")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"Error calling OpenAI API: {e}")
    print("The search found relevant documents but couldn't generate a response.")
    print("Here's the raw data found:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\nDocument {i+1}:")
        print(doc[:500] + "..." if len(doc) > 500 else doc)