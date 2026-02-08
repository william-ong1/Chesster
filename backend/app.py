# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Main Flask/FastAPI application for Chesster backend
# Exposes API endpoints for data upload, model training, and gameplay

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Import API modules
from api.upload import upload_bp
from api.training import training_bp
from api.agent import agent_bp
from auth.authentication import auth_bp

app = Flask(__name__)
CORS(app)

# Load configuration
app.config.from_object('config.config.DevelopmentConfig')

# Register blueprints
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(training_bp, url_prefix='/api')
app.register_blueprint(agent_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "chesster-backend"}), 200

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
