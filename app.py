from flask import Flask
from flask_cors import CORS
from interfaces.web.routes.__init__ import register_blueprints ,bp as main_bp 
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {"origins": ["http://localhost", "http://127.0.0.1", "http://example.com"]}
})

# Register the Blueprint
app.register_blueprint(main_bp)

# Register additional Blueprints
register_blueprints(app)

SECRET_KEY = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True)



