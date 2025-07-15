from flask import Blueprint, request, jsonify
from service.rag_service import RAGService
from flask_jwt_extended import jwt_required, get_jwt_identity

rag_bp = Blueprint('rag', __name__)
rag_service = RAGService()

@rag_bp.route('/search', methods=['POST'])
@jwt_required()
def search_documents():
    """Search for relevant documents without AI response"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "message": "Query is required"
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                "success": False,
                "message": "Query cannot be empty"
            }), 400
        
        n_results = data.get('n_results', 3)
        
        # Validate n_results
        if not isinstance(n_results, int) or n_results < 1 or n_results > 10:
            n_results = 3
        
        result = rag_service.search_documents(query, n_results)
        
        return jsonify(result), 200 if result["success"] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@rag_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    """Ask a question and get AI-powered response"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "message": "Query is required"
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                "success": False,
                "message": "Query cannot be empty"
            }), 400
        
        n_results = data.get('n_results', 3)
        use_ai = data.get('use_ai', True)
        
        # Validate n_results
        if not isinstance(n_results, int) or n_results < 1 or n_results > 10:
            n_results = 3
        
        result = rag_service.ask_question(query, n_results, use_ai)
        
        return jsonify(result), 200 if result["success"] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@rag_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get RAG database statistics"""
    try:
        result = rag_service.get_collection_stats()
        return jsonify(result), 200 if result["success"] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

# Public endpoint for testing (remove in production)
@rag_bp.route('/test', methods=['POST'])
def test_rag():
    """Test endpoint without authentication - remove in production"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "message": "Query is required"
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                "success": False,
                "message": "Query cannot be empty"
            }), 400
        
        n_results = data.get('n_results', 3)
        use_ai = data.get('use_ai', False)  # Default to False for testing
        
        result = rag_service.ask_question(query, n_results, use_ai)
        
        return jsonify(result), 200 if result["success"] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500
