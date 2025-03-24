from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from interfaces.web.routes.__init__ import register_blueprints, bp as main_bp
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

app = Flask(__name__)

# 全域性 CORS 設定
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Register the Blueprint
app.register_blueprint(main_bp)

# Register additional Blueprints
register_blueprints(app)

SECRET_KEY = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

# 處理 OPTIONS 請求
@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.status_code = 200
        return response

if __name__ == '__main__':
    app.run(debug=True)



