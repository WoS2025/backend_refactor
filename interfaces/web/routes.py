from flask import Blueprint, request, jsonify
import re
from infrastructure.repositories import Database
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
from service.workspace_service import WorkspaceService

# Initialize database and repository
db = Database()
repo = WorkspaceRepo()
service = WorkspaceService()

# Create a Blueprint for the routes
bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return "Hello, World!"

@bp.route('/workspaces', methods=['GET'])
def get_workspaces():
    workspaces = service.get_workspaces()
    return jsonify([workspace.to_dict() for workspace in workspaces]), 200

@bp.route('/workspaces', methods=['POST'])
def create_workspace():
    data = request.json
    if 'name' not in data:
        return jsonify({'error': 'Workspace name is required'}), 400
    if not re.match("^[a-zA-Z0-9_]*$", data['name']):
            return jsonify({"message": "工作區名稱僅可包含大小寫英文字母、數字、底線。其餘符號皆不符合規則。"}), 400
    response, status_code = service.create_workspace(data['name'])
    return jsonify(response), status_code

@bp.route('/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    workspace = service.get_workspace(workspace_id)
    if workspace:
        return jsonify(workspace.to_dict()), 200
    return jsonify({'error': 'Workspace not found'}), 404

@bp.route('/workspaces/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    result = service.delete_workspace(workspace_id)
    if result.deleted_count == 1:
        return '', 204
    return jsonify({'error': 'Workspace not found'}), 404

# request.json = {"file": [{ "name": "", "content": "" },{ "name": "", "content": "" }, ... ] }
@bp.route('/workspaces/<workspace_id>/files', methods=['PUT'])  # Changed to PUT
def add_file_to_workspace(workspace_id):
    data = request.json
    if 'file' not in data or not isinstance(data['file'], list):
        return jsonify({'error': 'File data with name and content is required'}), 400

    for file in data['file']:
        if 'name' not in file or 'content' not in file:
            return jsonify({'error': 'Each file must have a name and content'}), 400

        file_data = {
            'name': file['name'],
            'content': file['content']
        }

        result = service.add_file_to_workspace(workspace_id, file_data)
        if not result:
            return jsonify({'error': 'Workspace not found'}), 404

    return '', 204

@bp.route('/workspaces/<workspace_id>/files/<file_name>', methods=['DELETE'])
def remove_file_from_workspace(workspace_id, file_name):
    result = service.remove_file_from_workspace(workspace_id, file_name)
    if result:
        return '', 204
    return jsonify({'error': 'Workspace not found'}), 404

@bp.route('/workspaces/<workspace_id>/analysis/result', methods=['GET'])
def get_analysis_result(workspace_id):
    if not service.get_workspace(workspace_id):
        return jsonify({'error': 'Workspace not found'}), 404
    result = service.get_analysis(workspace_id)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404

# request.json = { "keyword": ""}
@bp.route('/workspaces/<workspace_id>/analysis/keyword', methods=['POST'])
def keyword_analysis(workspace_id):
    data = request.json
    if 'keyword' not in data:
        return jsonify({'error': 'Keyword is required'}), 400
    result = service.keyword_analysis(workspace_id, data['keyword'])
    return jsonify(result), 200

# request.json = {"start": '', "end": '', "threshold": ''}
@bp.route('/workspaces/<workspace_id>/analysis/keyword/year', methods=['POST'])
def keyword_year_analysis(workspace_id):
    data = request.json
    result = service.keyword_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:   
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404
# request.json = {'threshold': ''}
@bp.route('/workspaces/<workspace_id>/analysis/keyword/occurence', methods=['POST'])
def keyword_occurence_analysis(workspace_id):
    data = request.json
    result = service.keyword_analysis_occurence(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200 
    return jsonify({'error': 'no result'}), 404

# request.json = { "start": '', "end": '', "threshold": ''}
@bp.route('/workspaces/<workspace_id>/analysis/author/year', methods=['POST'])
def author_analysis_year(workspace_id):
    data = request.json
    result = service.author_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404

# request.json = {"threshold": 1}
@bp.route('/workspaces/<workspace_id>/analysis/reference', methods=['POST'])
def reference_analysis(workspace_id):
    data = request.json
    result = service.reference_analysis(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404

# request.json = {"field": ''}
@bp.route('/workspaces/<workspace_id>/analysis/field', methods=['POST'])
def field_analysis(workspace_id):
    data = request.json
    result = service.field_analysis(workspace_id, data['field'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404

# request.json = {"start": 2000, "end": 2025, "threshold": 1}
@bp.route('/workspaces/<workspace_id>/analysis/field/year', methods=['POST'])
def field_analysis_year(workspace_id):
    data = request.json
    result = service.field_analysis_year(workspace_id, data['start'], data['end'], data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404

# request.json = {"threshold": 1}
@bp.route('/workspaces/<workspace_id>/analysis/field/occurence', methods=['POST'])
def field_occurence_analysis(workspace_id):
    data = request.json
    result = service.field_analysis_occurence(workspace_id, data['threshold'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'no result'}), 404