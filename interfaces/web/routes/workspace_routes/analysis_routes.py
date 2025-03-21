from flask import Blueprint, request, jsonify, Response
import json
from service.workspace_service import WorkspaceService

workspace_service = WorkspaceService()
analysis_bp = Blueprint('analysis', __name__)

# 關鍵字分析
@analysis_bp.route('/keyword', methods=['POST'])
def keyword_analysis(workspace_id):
    data = request.json
    if 'keyword' not in data:
        return jsonify({'error': 'Keyword is required'}), 400
    result = workspace_service.keyword_analysis(workspace_id, data['keyword'])
    return jsonify(result), 200

# 關鍵字年份分析
@analysis_bp.route('/keyword/year', methods=['POST'])
def keyword_year_analysis(workspace_id):
    data = request.json
    result = workspace_service.keyword_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 關鍵字出現次數分析
@analysis_bp.route('/keyword/occurence', methods=['POST'])
def keyword_occurence_analysis(workspace_id):
    data = request.json
    result = workspace_service.keyword_analysis_occurence(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 作者年份分析
@analysis_bp.route('/author/year', methods=['POST'])
def author_analysis_year(workspace_id):
    data = request.json
    result = workspace_service.author_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 引用分析
@analysis_bp.route('/reference', methods=['POST'])
def reference_analysis(workspace_id):
    data = request.json
    result = workspace_service.reference_analysis(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 領域分析
@analysis_bp.route('/field', methods=['POST'])
def field_analysis(workspace_id):
    data = request.json
    result = workspace_service.field_analysis(workspace_id, data['field'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 領域年份分析
@analysis_bp.route('/field/year', methods=['POST'])
def field_analysis_year(workspace_id):
    data = request.json
    result = workspace_service.field_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 領域出現次數分析
@analysis_bp.route('/field/occurence', methods=['POST'])
def field_occurence_analysis(workspace_id):
    data = request.json
    result = workspace_service.field_analysis_occurence(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 機構分析
@analysis_bp.route('/institution', methods=['POST'])
def institution_analysis(workspace_id):
    data = request.json
    result = workspace_service.institution_analysis(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 機構年份分析
@analysis_bp.route('/institution/year', methods=['POST'])
def institution_analysis_by_year(workspace_id):
    data = request.json
    result = workspace_service.institution_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 獲取分析結果
@analysis_bp.route('/result', methods=['GET'])
def get_analysis_result(workspace_id):
    if not workspace_service.get_workspace(workspace_id):
        return jsonify({'error': 'Workspace not found'}), 404
    result = workspace_service.get_analysis(workspace_id)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'No result'}), 404

# 下載分析結果
@analysis_bp.route('/download', methods=['GET'])
def download_analysis(workspace_id):
    result = workspace_service.get_analysis(workspace_id)
    if not result:
        return jsonify({'error': 'No analysis result found'}), 404
    json_data = json.dumps(result, indent=4)
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename=analysis_{workspace_id}.json"}
    )