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
client = OpenAI()

# Chat history to remember conversation
chat_history = []

print(" RAG Chat Assistant - Federated Learning Research")
print("Ask me anything about federated learning research!")
print("Type 'quit', 'exit', or 'bye' to end the conversation.\n")

def add_to_history(role, content):
    """Add message to chat history"""
    chat_history.append({"role": role, "content": content})
    # Keep only last 10 messages to avoid token limits
    if len(chat_history) > 10:
        chat_history.pop(0)

def get_rag_context(query):
    """Get relevant documents from RAG system"""
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    
    if not results['documents'][0]:
        return "No relevant documents found in the database."
    
    # Combine all documents into context
    context = ""
    for i, doc in enumerate(results['documents'][0]):
        context += f"\n--- Document {i+1} ---\n{doc}\n"
    
    return context

# Main chat loop
while True:
    try:
        user_query = input("\n💬 You: ").strip()
        
        # Check for exit commands
        if user_query.lower() in ['quit', 'exit', 'bye', 'q']:
            print("\n👋 Goodbye! Thanks for chatting!")
            break
        
        if not user_query:
            print("Please enter a question.")
            continue
        
        # Add user message to history
        add_to_history("user", user_query)
        
        # Get RAG context
        rag_context = get_rag_context(user_query)
        
        # Create system prompt with context
        system_prompt = f"""
You are a helpful assistant for federated learning research. You can answer based on the provided research data and also use your general knowledge about federated learning.

Current Research Data:
{rag_context}

Instructions:
- Answer the user's question using the research data when relevant
- Maintain conversation context from previous messages
- Be conversational and helpful
- If asked about previous conversation, refer to the chat history
"""

        # Prepare messages for OpenAI (system + history + current)
        messages = [{"role": "system", "content": system_prompt}] + chat_history
        
        print("\nWOS Assistant: ", end="", flush=True)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True  # Enable streaming for real-time response
        )
        
        # Stream the response
        assistant_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                assistant_response += content
        
        print()  # New line after response
        
        # Add assistant response to history
        add_to_history("assistant", assistant_response)
        
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please try again.")

print("\n📊 Chat Summary:")
print(f"Total messages in this conversation: {len(chat_history)}")