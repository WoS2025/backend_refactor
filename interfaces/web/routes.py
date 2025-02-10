from flask import Blueprint, request, jsonify
from infrastructure.repositories import Database
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
from service.workspace_service import WorkspaceService

# Initialize database and repository
db = Database()
repo = WorkspaceRepo(db)
service = WorkspaceService(repo)

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
    workspace_id = service.create_workspace(data['name'])
    return jsonify({'workspace_id': workspace_id}), 201

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

@bp.route('/workspaces/<workspace_id>/files', methods=['POST'])
def add_file_to_workspace(workspace_id):
    data = request.json
    if 'file' not in data:
        return jsonify({'error': 'File data is required'}), 400
    result = service.add_file_to_workspace(workspace_id, data['file'])
    if result:
        return '', 204
    return jsonify({'error': 'Workspace not found'}), 404

@bp.route('/workspaces/<workspace_id>/files/<file_name>', methods=['DELETE'])
def remove_file_from_workspace(workspace_id, file_name):
    result = service.remove_file_from_workspace(workspace_id, file_name)
    if result:
        return '', 204
    return jsonify({'error': 'Workspace not found'}), 404

@bp.route('/workspaces/<workspace_id>/analysis', methods=['GET'])
def get_analysis(workspace_id):
    result = service.get_analysis(workspace_id)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Workspace not found'}), 404

@bp.route('/analysis/author', methods=['POST'])
def author_analysis():
    data = request.json
    if 'workspace_id' not in data:
        return jsonify({'error': 'Workspace ID is required'}), 400
    result = service.get_author_analysis(data['workspace_id'])
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Workspace not found'}), 404
