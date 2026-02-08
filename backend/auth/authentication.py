# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Authentication endpoints for user management
# POST /api/auth/register - Create new user account
# POST /api/auth/login - User login with JWT token generation
# GET /api/auth/verify - Verify JWT token

from flask import Blueprint, request, jsonify
import jwt
import bcrypt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# TODO: Move to config
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
    {
        "username": str,
        "email": str,
        "password": str
    }
    
    Returns:
    {
        "success": bool,
        "user_id": str,
        "token": str
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
        
        # TODO: Implement user registration
        # 1. Check if user exists
        # 2. Hash password with bcrypt
        # 3. Store in MongoDB users collection
        # 4. Generate JWT token
        
        return jsonify({
            "success": True,
            "user_id": "placeholder_user_id",
            "token": "placeholder_token",
            "message": "Registration endpoint - implementation pending"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    
    Request body:
    {
        "username": str,
        "password": str
    }
    
    Returns:
    {
        "success": bool,
        "token": str,
        "user_id": str
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        
        # TODO: Implement user login
        # 1. Retrieve user from MongoDB
        # 2. Verify password with bcrypt
        # 3. Generate JWT token
        # 4. Update last_login timestamp
        
        return jsonify({
            "success": True,
            "token": "placeholder_token",
            "user_id": "placeholder_user_id",
            "message": "Login endpoint - implementation pending"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    Verify JWT token from Authorization header
    
    Returns:
    {
        "valid": bool,
        "user_id": str
    }
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401
        
        # TODO: Implement token verification
        # 1. Extract token from "Bearer <token>"
        # 2. Verify JWT signature
        # 3. Check expiration
        # 4. Return user_id from payload
        
        return jsonify({
            "valid": True,
            "user_id": "placeholder_user_id",
            "message": "Verify endpoint - implementation pending"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401
