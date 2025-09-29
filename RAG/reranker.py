"""
Modern Reranking Module for RAG system
Using BGE Reranker models for improved document relevance scoring
"""

import torch
from typing import List, Tuple, Dict, Any
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

class BGEReranker:
    """
    BGE (BAAI General Embedding) Reranker for document reranking
    Uses cross-encoder architecture for precise query-document relevance scoring
    """
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: str = "auto",
        max_length: int = 512,
        batch_size: int = 8
    ):
        """
        Initialize BGE Reranker
        
        Args:
            model_name: BGE reranker model to use
            device: Device to run inference on
            max_length: Maximum sequence length
            batch_size: Batch size for processing
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        
        # Auto-detect device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Loading BGE Reranker: {model_name} on {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"BGE Reranker loaded successfully")
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = None
    ) -> List[Tuple[str, float]]:
        """
        Rerank documents based on query relevance
        
        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of top documents to return (None for all)
            
        Returns:
            List of (document, score) tuples sorted by relevance
        """
        if not documents:
            return []
            
        # Score all documents
        scores = self._compute_scores(query, documents)
        
        # Create document-score pairs
        doc_score_pairs = list(zip(documents, scores))
        
        # Sort by score (descending)
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k if specified
        if top_k is not None:
            doc_score_pairs = doc_score_pairs[:top_k]
            
        return doc_score_pairs
    
    def _compute_scores(self, query: str, documents: List[str]) -> List[float]:
        """
        Compute relevance scores for query-document pairs
        
        Args:
            query: Search query
            documents: List of document texts
            
        Returns:
            List of relevance scores
        """
        all_scores = []
        
        # Process documents in batches
        for i in range(0, len(documents), self.batch_size):
            batch_docs = documents[i:i + self.batch_size]
            batch_scores = self._score_batch(query, batch_docs)
            all_scores.extend(batch_scores)
            
        return all_scores
    
    def _score_batch(self, query: str, documents: List[str]) -> List[float]:
        """
        Score a batch of documents
        
        Args:
            query: Search query
            documents: Batch of document texts
            
        Returns:
            List of relevance scores for the batch
        """
        # Prepare input pairs
        pairs = [(query, doc) for doc in documents]
        
        # Tokenize
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        ).to(self.device)
        
        # Get scores
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use logits as relevance scores
            scores = outputs.logits.squeeze(-1).cpu().tolist()
            
        # Handle single document case
        if isinstance(scores, float):
            scores = [scores]
            
        return scores

class SimpleReranker:
    """
    Simple reranking based on BM25 or TF-IDF scoring
    Fallback option when transformer models are not available
    """
    
    def __init__(self, method: str = "bm25"):
        """
        Initialize Simple Reranker
        
        Args:
            method: Scoring method ('bm25' or 'tfidf')
        """
        self.method = method
        logger.info(f"Initialized Simple Reranker with {method}")
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = None
    ) -> List[Tuple[str, float]]:
        """
        Simple reranking based on keyword matching
        
        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of top documents to return
            
        Returns:
            List of (document, score) tuples
        """
        if not documents:
            return []
        
        # Simple scoring based on query term overlap
        query_terms = set(query.lower().split())
        doc_scores = []
        
        for doc in documents:
            doc_terms = set(doc.lower().split())
            # Simple Jaccard similarity
            intersection = len(query_terms & doc_terms)
            union = len(query_terms | doc_terms)
            score = intersection / union if union > 0 else 0.0
            doc_scores.append((doc, score))
        
        # Sort by score
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k if specified
        if top_k is not None:
            doc_scores = doc_scores[:top_k]
            
        return doc_scores

def create_reranker(
    reranker_type: str = "bge",
    model_name: str = "BAAI/bge-reranker-v2-m3",
    **kwargs
) -> Any:
    """
    Factory function to create reranker instances
    
    Args:
        reranker_type: Type of reranker ('bge', 'simple')
        model_name: Model name for BGE reranker
        **kwargs: Additional arguments
        
    Returns:
        Reranker instance
    """
    if reranker_type == "bge":
        try:
            return BGEReranker(model_name=model_name, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to load BGE reranker: {e}")
            logger.info("Falling back to simple reranker")
            return SimpleReranker()
    elif reranker_type == "simple":
        return SimpleReranker(**kwargs)
    else:
        raise ValueError(f"Unknown reranker type: {reranker_type}")

# Example usage and testing
if __name__ == "__main__":
    # Test the reranker
    reranker = create_reranker("bge")
    
    query = "federated learning privacy"
    documents = [
        "Federated learning enables privacy-preserving machine learning",
        "Deep learning models require large datasets",
        "Privacy protection is crucial in federated systems",
        "Machine learning applications in healthcare"
    ]
    
    results = reranker.rerank(query, documents, top_k=3)
    
    print("Reranking Results:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   Doc: {doc[:100]}...")
        print()
