from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from infrastructure import database

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

db = database.Database()

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/')



