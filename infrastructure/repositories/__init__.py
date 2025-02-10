import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Database:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri:
            raise ValueError("No MongoDB URI found in environment variables")
        self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        self.db = self.client.get_database()

    def get_collection(self, collection_name):
        return self.db[collection_name]

# Example usage:
# db_instance = Database()
# collection = db_instance.get_collection('your_collection_name')