from datetime import datetime

class User:
    def __init__(self, user_id, username, email, password, created_at=None, workspace_ids=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at or datetime.now()
        self.workspace_ids = workspace_ids

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'workspace_ids': self.workspace_ids
        }

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