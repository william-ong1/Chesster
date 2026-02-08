# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Authentication endpoints for user management
# Handles user registration, login, and JWT token management

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import sys
import uuid

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from data.database_manager import DatabaseManager

# Initialize blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize database manager
db = DatabaseManager()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account
    
    Request body:
        {
            "username": str (required),
            "email": str (required),
            "password": str (required, min 8 characters)
        }
    
    Returns:
        201: {
            "access_token": str (JWT token),
            "user": {
                "user_id": str,
                "username": str,
                "email": str,
                "created_at": str
            }
        }
        
        400: {"error": str} - Validation error
        409: {"error": str} - User already exists
        500: {"error": str} - Server error
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({"error": "username, email, and password are required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        
        if '@' not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if user already exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({"error": "Username already taken"}), 409
        
        existing_email = db.get_user_by_email(email)
        if existing_email:
            return jsonify({"error": "Email already registered"}), 409
        
        # Generate unique user_id
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create user in database
        success = db.create_user(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        if not success:
            return jsonify({"error": "Failed to create user"}), 500
        
        # Generate JWT token
        access_token = create_access_token(
            identity=user_id,
            additional_claims={"username": username}
        )
        
        # Get user data (without password hash)
        user = db.get_user_by_id(user_id)
        user_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"].isoformat()
        }
        
        print(f"✅ User registered: {username} ({user_id})")
        
        return jsonify({
            "access_token": access_token,
            "user": user_data
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login with credentials
    
    Request body:
        {
            "email": str (required),
            "password": str (required)
        }
    
    Returns:
        200: {
            "access_token": str (JWT token),
            "user": {
                "user_id": str,
                "username": str,
                "email": str
            }
        }
        
        400: {"error": str} - Validation error
        401: {"error": str} - Invalid credentials
        500: {"error": str} - Server error
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400
        
        # Retrieve user from database
        user = db.get_user_by_email(email)
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Update last login timestamp
        db.update_last_login(user['user_id'])
        
        # Generate JWT token
        access_token = create_access_token(
            identity=user['user_id'],
            additional_claims={"username": user['username']}
        )
        
        # Prepare user data (without password hash)
        user_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
        
        print(f"✅ User logged in: {user['username']} ({user['user_id']})")
        
        return jsonify({
            "access_token": access_token,
            "user": user_data
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information
    
    Headers:
        Authorization: Bearer <JWT token>
    
    Returns:
        200: {
            "user_id": str,
            "username": str,
            "email": str,
            "created_at": str,
            "last_login": str
        }
        
        401: {"error": str} - Unauthorized
        404: {"error": str} - User not found
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT token
        user_id = get_jwt_identity()
        
        # Retrieve user from database
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Prepare user data (without password hash)
        user_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"].isoformat(),
            "last_login": user["last_login"].isoformat() if user.get("last_login") else None
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify JWT token validity
    
    Headers:
        Authorization: Bearer <JWT token>
    
    Returns:
        200: {
            "valid": true,
            "user_id": str,
            "username": str
        }
        
        401: {"error": str} - Invalid or expired token
    """
    try:
        # Get user_id and claims from JWT
        user_id = get_jwt_identity()
        jwt_claims = get_jwt()
        
        return jsonify({
            "valid": True,
            "user_id": user_id,
            "username": jwt_claims.get("username", "")
        }), 200
        
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return jsonify({"error": "Invalid token"}), 401
