from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from infrastructure import database

server = Flask(__name__)
CORS(server, supports_credentials=True, resources={r"/*": {"origins": "*"}})

db = database.Database()

@server.route('/')
def home():
    return "Hello, World!"

@server.route('/')



