from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import secrets
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, decode_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
load_dotenv()  # Load environment variables from .env file
SECRET_KEY = os.getenv('SECRET_KEY')

class User:
    def __init__(self, user_id, username, email, password, created_at=None, workspace_ids=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at or datetime.now()
        self.workspace_ids = workspace_ids or []

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'workspace_ids': self.workspace_ids
        }

    def generate_jwt(self):
        # 使用 flask_jwt_extended 的 create_access_token
        additional_claims = {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'workspace_ids': self.workspace_ids
        }
        return create_access_token(identity=self.user_id, additional_claims=additional_claims)

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data.get('user_id'),
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            created_at=data.get('created_at'),
            workspace_ids=data.get('workspace_ids')
        )
