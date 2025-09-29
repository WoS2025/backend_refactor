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
    """Get relevant documents from RAG system with reranking"""
    # First stage: ChromaDB retrieval (wider recall)
    results = collection.query(
        query_texts=[query],
        n_results=10  # Get more candidates for reranking
    )
    
    if not results['documents'][0]:
        return "No relevant documents found in the database."
    
    # Get documents and their initial distances
    documents = results['documents'][0]
    distances = results['distances'][0]
    
    # More lenient distance threshold for better recall
    relevance_threshold = 1.8  # Increased from 1.2
    filtered_docs = []
    for doc, distance in zip(documents, distances):
        if distance < relevance_threshold:
            filtered_docs.append(doc)
    
    # If still no results, use top 5 regardless of distance
    if not filtered_docs:
        filtered_docs = documents[:5]
    
    # Second stage: Reranking for better relevance
    try:
        # Try to use BGE reranker if available
        from reranker import create_reranker
        reranker = create_reranker("bge")
        
        # Rerank the filtered documents
        reranked_results = reranker.rerank(
            query=query, 
            documents=filtered_docs, 
            top_k=3  # Final top-k results
        )
        
        # Combine reranked results into context
        context = ""
        for i, (doc, score) in enumerate(reranked_results, 1):
            context += f"\n--- Document {i} (Relevance: {score:.4f}) ---\n{doc}\n"
            
    except ImportError:
        # Fallback: use original ChromaDB ranking
        context = ""
        for i, doc in enumerate(filtered_docs[:3], 1):  # Take top 3
            context += f"\n--- Document {i} ---\n{doc}\n"
    except Exception as e:
        # If reranker fails, fallback gracefully
        print(f"⚠️  Reranker failed: {e}")
        context = ""
        for i, doc in enumerate(filtered_docs[:3], 1):
            context += f"\n--- Document {i} ---\n{doc}\n"
    
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

        # Create system prompt with embedded RAG context (prompt only change per user request)
        system_prompt = f"""
Role: Federated Learning Analysis Assistant

Primary Objective:
Provide a precise, helpful answer about federated learning using the retrieved documents FIRST. Only augment with general, well‑established domain knowledge when the documents are incomplete.

Answer Policy:
1. If the answer (即使只有部分) 出現在檢索內容，直接摘錄或轉述（引用段落勿超過 40 中文 / 30 English words）。
2. 若文件僅提供部分線索，整合並標示：哪一部分是直接證據 (Evidence)；哪一部分是你的合理由來 (Synthesis)。
3. 若文件未直接給出答案，先寫：『資料中未直接找到完整答案，以下為根據一般聯邦式學習知識的推論：』然後給審慎推論。
4. 僅在 (a) 檢索結果為空或明顯不相關 且 (b) 無法基於通用原理做出可信推斷 時，才以『我不知道』/ 'I don't know' 回覆，並說明缺少哪些資訊與建議下一步查詢方向。
5. 能說明需要哪些資料時，不可以只回答『我不知道』。

Output Structure (依使用者語言；使用者中文就用中文)：
- 摘要 / Summary (1–2 句)
- 依據資料 / Evidence: 條列（標示 [Doc i]）
- 推論 / Inference（如有）
- 建議下一步 / Next Steps（選擇性）

Style:
- 簡潔、分析式，避免重複；必要時標示 (估計) / (assumption)
- 不捏造精確數值；若需概略，明確標示為估計
- 保留關鍵技術詞 (non-iid, aggregation, privacy, personalization, heterogeneity)

Retrieved Context (RAG 摘要，可能含雜訊，需判斷可靠性):
{rag_context}

Instructions:
- 優先使用檢索資料回答；不足時再補一般領域知識
- 維持對話脈絡（使用前面歷史）
- 不要只說『我不知道』，除非符合嚴格條件
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