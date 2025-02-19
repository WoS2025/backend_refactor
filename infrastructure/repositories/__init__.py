import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from werkzeug.security import generate_password_hash
from domain.models.user import User
load_dotenv()  # Load environment variables from .env file

class Database:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            raise ValueError("No MongoDB URI found in environment variables")
        self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        self.db = self.client.get_database('Uniproject')  # Explicitly specify the database name

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def add_workspace(self, workspace_id, workspace_name):
        collection = self.get_collection('workspaces')
        if collection.find_one({'name': workspace_name}):
            return {"status": "error", "message": "The name already exists"}
        try:
            data = collection.insert_one({'workspace_id': workspace_id, 'name': workspace_name, 'files': [], 'created_at': datetime.now()})
            return data
        except DuplicateKeyError:
            return {"status": "error", "message": "Workspace ID already exists"}
        
    def add_user(self, user_id, username, email, password):
        collection = self.get_collection('users')
        if collection.find_one({'email': email}):
            return {"status": "error", "message": "Email already registered"}
        hashed_password = generate_password_hash(password)
        user = User(user_id, username, email, hashed_password)
        try:
            collection.insert_one(user.to_dict())
            return {"status": "success", "message": "User registered successfully"}
        except DuplicateKeyError:
            return {"status": "error", "message": "User ID already exists"}
        
    

# Example usage:
# db_instance = Database()
# response = db_instance.add_workspace('workspace_id', 'workspace_name')
# print(response)