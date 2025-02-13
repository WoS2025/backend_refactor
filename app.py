from flask import Flask
from flask_cors import CORS
from interfaces.web.routes import bp as main_bp

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Register the Blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)



