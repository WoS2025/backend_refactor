import uuid
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from domain.models.user import User
from infrastructure.repositories import Database
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class UserRepository:
    def __init__(self):
        self.db = Database()
        self.collection = self.db.get_collection('users')

    def register_user(self, username, email, password):
        if self.collection.find_one({'email': email}):
            return {"status": "error", "message": "Email already registered"}
        user_id = str(uuid.uuid4())  # Generate a unique user_id
        hashed_password = generate_password_hash(password)
        user = User(user_id, username, email, hashed_password)
        try:
            self.collection.insert_one(user.to_dict())
            return {"status": "success", "message": "User registered successfully"}
        except DuplicateKeyError:
            return {"status": "error", "message": "User ID already exists"}

    def login_user(self, email, password):
        user_data = self.collection.find_one({'email': email})
        if not user_data:
            return {"status": "error", "message": "Email not found"}
        user = User.from_dict(user_data)
        if check_password_hash(user.password, password): 
            return {"status": "success", "message": "Login successful", "user": user.to_dict()}
        else:
            return {"status": "error", "message": "Invalid password"}
        
    def get_user(self, user_id):
        user_data = self.collection.find_one({'user_id': user_id})
        if not user_data:
            return {"status": "error", "message": "User not found"}
        user = User.from_dict(user_data)
        return {"status": "success", "message": "User found", "user": user.to_dict()}
        
    def update_password(self, email, password):
        user_data = self.collection.find_one({'email': email})
        if not user_data:
            return {"status": "error", "message": "Email not found"}
        user = User.from_dict(user_data)
        hashed_password = generate_password_hash(password)
        user.password = hashed_password
        result = self.collection.update_one({'email': email}, {'$set': {'password': hashed_password}})
        if result.modified_count > 0:
            return {"status": "success", "message": "Password updated successfully"}
        else:
            return {"status": "error", "message": "Failed to update password"}

    def find_user_by_email(self, email):
        user_data = self.collection.find_one ({'email': email})
        if not user_data:
            return None
        user = User.from_dict(user_data)
        return {"status": "success", "message": "User found", "user": user.to_dict()}
    
    def add_workspace_to_user(self, user_id, workspace_id):
        user_data = self.collection.find_one({'user_id': user_id})
        if not user_data:
            return {"status": "error", "message": "User not found"}
        user = User.from_dict(user_data)
        if workspace_id not in user.workspace_ids:
            user.workspace_ids.append(workspace_id)
            result = self.collection.update_one({'user_id': user_id}, {'$set': user.to_dict()})
            if result.modified_count > 0:
                return {"status": "success", "message": "Workspace added to user"}
            else:
                return {"status": "error", "message": "Failed to add workspace to user"}
        return {"status": "error", "message": "Workspace already added to user"}

    def remove_workspace_from_user(self, user_id, workspace_id):
        user_data = self.collection.find_one({'user_id': user_id})
        if not user_data:
            return {"status": "error", "message": "User not found"}
        user = User.from_dict(user_data)
        if workspace_id in user.workspace_ids:
            user.workspace_ids.remove(workspace_id)
            result = self.collection.update_one({'user_id': user_id}, {'$set': user.to_dict()})
            if result.modified_count > 0:
                return {"status": "success", "message": "Workspace removed from user"}
            else:
                return {"status": "error", "message": "Failed to remove workspace from user"}
        return {"status": "error", "message": "Workspace not found in user"}
    
    

# Example usage:
# user_repo = UserRepository()
# register_response = user_repo.register_user('username', 'email@example.com', 'password')
# print(register_response)
# login_response = user_repo.login_user('email@example.com', 'password')
# print(login_response)