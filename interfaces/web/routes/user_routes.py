from flask import Blueprint, request, jsonify
import re
from service.auth_service import AuthService

auth_service = AuthService()
user_bp = Blueprint('user', __name__)

# test route
@user_bp.route('/', methods=['GET'])
def home():
    return "Hello, user!"


@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not all(key in data for key in ('username', 'email', 'password')):
        return jsonify({'error': 'All fields are required'}), 400
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', data['email']) is None:
        return jsonify({"message": "Email格式不正確"}), 400
    response = auth_service.register_user(data['username'], data['email'], data['password'])
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    if not all(key in data for key in ('email', 'password')):
        return jsonify({'error': 'Email and password are required'}), 400
    response = auth_service.login_user(data['email'], data['password'])
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/user/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    response = auth_service.forgot_password(data['email'])
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/user/<email>/update-password', methods=['POST'])
def update_password(email):
    data = request.json
    if 'password' not in data:
        return jsonify({'error': 'Password is required'}), 400
    response = auth_service.update_password(email, data['password'])
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/<user_id>', methods=['GET'])
def get_user_workspaces(user_id):
    response = auth_service.get_user(user_id)
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/<user_id>/workspace/<workspace_id>', methods=['GET'])
def add_workspace_to_user(user_id, workspace_id):
    response = auth_service.add_workspace_to_user(user_id, workspace_id)
    return jsonify(response), 200 if response['status'] == 'success' else 400

@user_bp.route('/<user_id>/workspace/<workspace_id>', methods=['DELETE'])
def remove_workspace_from_user(user_id, workspace_id):
    response = auth_service.remove_workspace_from_user(user_id, workspace_id)
    return jsonify(response), 200 if response['status'] == 'success' else 400

# from flask_jwt_extended import jwt_required

# @user_bp.route('/<email>', methods=['GET'])
# @jwt_required()
# def get_user_workspaces(email):
#     response = auth_service.get_user(email)
#     return jsonify(response), 200 if response['status'] == 'success' else 400
    