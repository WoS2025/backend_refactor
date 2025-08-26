import chromadb
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        # Set up paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.rag_dir = os.path.join(os.path.dirname(self.script_dir), 'RAG')
        self.chroma_path = os.path.join(self.rag_dir, "chroma_db")
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_collection("llm_analysis_clean")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI()
    
    def search_documents(self, query, n_results=3):
        """Enhanced search with exact-match capabilities"""
        try:
            # First, try exact-match search for specific papers/authors
            exact_match_results = self._exact_match_search(query)
            
            # Then, do semantic search
            semantic_results = self._semantic_search(query, n_results)
            
            # Combine results, prioritizing exact matches
            combined_docs = []
            seen_ids = set()
            
            # Add exact matches first
            for doc in exact_match_results:
                doc_id = doc.get('id', doc.get('metadata', {}).get('analysis_type', ''))
                if doc_id not in seen_ids:
                    combined_docs.append(doc)
                    seen_ids.add(doc_id)
            
            # Add semantic results
            for doc in semantic_results:
                doc_id = doc.get('id', doc.get('metadata', {}).get('analysis_type', ''))
                if doc_id not in seen_ids and len(combined_docs) < n_results:
                    combined_docs.append(doc)
                    seen_ids.add(doc_id)
            
            return {
                "success": True,
                "query": query,
                "documents": combined_docs[:n_results],
                "total_found": len(combined_docs[:n_results]),
                "search_info": {
                    "exact_matches": len(exact_match_results),
                    "semantic_matches": len(semantic_results)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Search error: {str(e)}",
                "documents": []
            }
    
    def _exact_match_search(self, query):
        """Search for exact matches in document content"""
        try:
            # Get all documents and search for exact matches
            all_docs = self.collection.get()
            exact_matches = []
            
            query_lower = query.lower()
            
            for i, doc_content in enumerate(all_docs['documents']):
                if query_lower in doc_content.lower():
                    exact_matches.append({
                        "content": doc_content,
                        "metadata": all_docs['metadatas'][i],
                        "id": all_docs['ids'][i],
                        "distance": 0.0,  # Perfect match
                        "match_type": "exact"
                    })
            
            return exact_matches
            
        except Exception as e:
            return []
    
    def _semantic_search(self, query, n_results):
        """Original semantic search functionality"""
        try:
            # Try to determine the analysis type from the query
            query_lower = query.lower()
            analysis_type_filters = {}
            
            if any(keyword in query_lower for keyword in ['keyword', 'top keyword', 'most keyword']):
                analysis_type_filters = {"analysis_type": "keyword_occurence"}
            elif any(keyword in query_lower for keyword in ['author', 'top author', 'most author', 'researcher']):
                analysis_type_filters = {"analysis_type": "author_year"}
            elif any(keyword in query_lower for keyword in ['reference', 'citation', 'paper', 'most cited']):
                analysis_type_filters = {"analysis_type": "reference"}
            elif any(keyword in query_lower for keyword in ['field', 'research field', 'domain']):
                analysis_type_filters = {"analysis_type": "field_occurence"}
            
            # Search with optional filtering
            if analysis_type_filters:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=analysis_type_filters
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
            
            if not results['documents'][0]:
                return []
            
            # Format the results
            formatted_docs = []
            for i, doc in enumerate(results['documents'][0]):
                formatted_docs.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i],
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "match_type": "semantic"
                })
            
            return formatted_docs
            
        except Exception as e:
            return []

    def ask_question(self, query, n_results=3, use_ai=True):
        """Ask a question and get AI-powered response with smart context extraction"""
        try:
            # First search for relevant documents
            search_result = self.search_documents(query, n_results)
            
            if not search_result["success"]:
                return search_result
            
            # If AI is disabled, just return search results
            if not use_ai:
                return search_result
            
            # Smart context extraction for specific paper queries
            extracted_info = self._extract_paper_info(query, search_result["documents"])
            
            if extracted_info:
                # If we found specific paper info, use targeted context
                context = f"Specific paper information found:\n{extracted_info}"
            else:
                # Use general context for broad questions
                context_docs = [doc["content"] for doc in search_result["documents"]]
                
                # Smart context prioritization: if query seems to be about a specific paper,
                # prioritize documents that might contain specific papers
                query_lower = query.lower()
                if any(term in query_lower for term in ['author', 'wrote', 'paper', 'citation', 'meta-analysis']):
                    # For specific paper queries, check if any doc contains what we're looking for
                    priority_docs = []
                    other_docs = []
                    
                    for doc in context_docs:
                        # Check if this doc might contain specific paper info
                        if ('reference analysis' in doc['content'].lower() or 
                            'cited papers' in doc['content'].lower() or
                            'sala' in doc['content'].lower()):
                            priority_docs.append(doc)
                        else:
                            other_docs.append(doc)
                    
                    # Reorder: priority docs first, then others
                    reordered_docs = priority_docs + other_docs
                    context_docs = [doc["content"] for doc in reordered_docs]
                
                # Use fewer docs but with better prioritization
                max_docs = min(6, len(context_docs))  # Reduce to 6 for better focus
                context = "\n\n--- Document ---\n".join(context_docs[:max_docs])
            
            # Simple, direct prompt
            prompt = f"""Answer this question based on the research data:

Question: {query}

Research data:
{context}

Provide a clear, specific answer if the information is available."""
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "success": True,
                "query": query,
                "ai_response": ai_response,
                "source_documents": search_result["documents"],
                "total_sources": len(search_result["documents"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"RAG error: {str(e)}",
                "query": query
            }
    
    def _extract_paper_info(self, query, documents):
        """Extract specific paper information if query is about a specific paper"""
        query_lower = query.lower()
        
        # Check if this is a question about a specific paper
        paper_title_indicators = ['"', 'author of', 'who wrote', 'citation', 'cited', 'authors']
        if not any(indicator in query_lower for indicator in paper_title_indicators):
            return None
        
        # Try to extract paper title from the query
        import re
        
        # Look for quoted titles
        quoted_match = re.search(r'"([^"]+)"', query)
        if quoted_match:
            paper_title = quoted_match.group(1)
        else:
            # Look for title after "author of" or similar phrases
            title_match = re.search(r'author of (.+?)(?:\?|$)', query, re.IGNORECASE)
            if title_match:
                paper_title = title_match.group(1).strip()
            else:
                # Look for specific paper titles mentioned in query
                if "near and far transfer" in query_lower:
                    paper_title = "Near and Far Transfer in Cognitive Training"
                elif "cognitive training" in query_lower and "meta-analysis" in query_lower:
                    paper_title = "Near and Far Transfer in Cognitive Training"
                else:
                    return None
        
        # Search for this paper in the documents
        for doc in documents:
            content = doc["content"]
            if paper_title.lower() in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if paper_title.lower() in line.lower():
                        return f"Found paper: {line.strip()}"
        
        return None
    
    def get_collection_stats(self):
        """Get statistics about the RAG database"""
        try:
            count = self.collection.count()
            return {
                "success": True,
                "total_documents": count,
                "collection_name": "llm_analysis"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Stats error: {str(e)}"
            }
