# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Main Flask application for Chesster backend
# Exposes API endpoints for data upload, model training, and gameplay

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import API blueprints
from backend.api.upload import upload_bp
from backend.api.training import training_bp
from backend.api.agent import agent_bp
from backend.auth.authentication import auth_bp

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('FRONTEND_URL', 'http://localhost:5173').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize JWT
jwt = JWTManager(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri=os.getenv('REDIS_URL', 'memory://'),
    strategy="fixed-window"
)

# Apply rate limits to specific blueprints
limiter.limit("20 per minute")(auth_bp)  # Strict limit for auth endpoints
limiter.limit("30 per minute")(upload_bp)  # Moderate limit for uploads
limiter.limit("100 per minute")(agent_bp)  # Higher limit for gameplay

# Register blueprints
# Each blueprint handles a specific domain of the API
app.register_blueprint(auth_bp, url_prefix='/api/auth')  # Authentication endpoints
app.register_blueprint(upload_bp, url_prefix='/api')     # Data upload endpoints
app.register_blueprint(training_bp, url_prefix='/api')   # Model training endpoints
app.register_blueprint(agent_bp, url_prefix='/api')      # Agent/gameplay endpoints

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "chesster-backend",
        "version": "0.1.0"
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API information
    
    Returns:
        JSON response with available endpoints
    """
    return jsonify({
        "service": "Chesster Backend API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth/*",
            "upload": "/api/upload",
            "training": "/api/training/*",
            "agent": "/api/agent/*"
        },
        "docs": "See README.md for API documentation"
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file upload size errors"""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

# JWT error handlers
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    """Handle missing JWT token"""
    return jsonify({"error": "Missing authorization token"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    """Handle invalid JWT token"""
    return jsonify({"error": "Invalid authorization token"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT token"""
    return jsonify({"error": "Token has expired"}), 401

# Request logging middleware
@app.before_request
def log_request():
    """Log incoming requests for debugging"""
    if os.getenv('FLASK_DEBUG', 'False') == 'True':
        print(f"📨 {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log outgoing responses for debugging"""
    if os.getenv('FLASK_DEBUG', 'False') == 'True':
        print(f"📤 {request.method} {request.path} -> {response.status_code}")
    return response

# Run application
if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"🚀 Starting Chesster Backend Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   MongoDB: {app.config['MONGO_URI']}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
