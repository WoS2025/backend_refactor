from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from service.rag_service import RAGService

# Create Blueprint for simple RAG routes (no authentication required)
simple_rag_bp = Blueprint('simple_rag', __name__)
rag_service = RAGService()

@simple_rag_bp.route('/chat', methods=['POST', 'OPTIONS'])
@cross_origin()
def chat():
    """Simple chat endpoint for frontend - no authentication required"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        user_message = data['message']
        use_ai = data.get('use_ai', True)
        n_results = data.get('n_results', 3)
        
        # Call RAG service
        result = rag_service.ask_question(user_message, n_results, use_ai)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result.get('ai_response', 'No AI response generated'),
                "sources": result.get('source_documents', []),
                "total_sources": result.get('total_sources', 0),
                "query": result.get('query', user_message)
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('message', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@simple_rag_bp.route('/search', methods=['POST', 'OPTIONS'])
@cross_origin()
def search():
    """Simple search endpoint - returns documents without AI processing"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        
        # Call RAG service for search only
        result = rag_service.search_documents(query, n_results)
        
        if result['success']:
            return jsonify({
                "success": True,
                "documents": result['documents'],
                "total_found": result['total_found'],
                "query": query
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('message', 'No documents found')
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@simple_rag_bp.route('/status', methods=['GET'])
@cross_origin()
def status():
    """Check RAG system status"""
    try:
        stats = rag_service.get_collection_stats()
        
        if stats['success']:
            return jsonify({
                "success": True,
                "status": "RAG system is running",
                "total_documents": stats['total_documents'],
                "collection_name": stats['collection_name']
            })
        else:
            return jsonify({
                "success": False,
                "error": "RAG system error"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"System error: {str(e)}"
        }), 500
