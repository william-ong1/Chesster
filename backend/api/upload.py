# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for uploading chess game data
# POST /api/upload-pgn - Upload PGN files for a user

from flask import Blueprint, request, jsonify
import sys
sys.path.append('../data')
from data.PGN_cleaner import clean_pgn
from data.PGN_to_board_state import pgn_to_board_states

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload-pgn', methods=['POST'])
def upload_pgn():
    """
    Upload PGN game data for a user
    
    Request body:
    {
        "user_id": str,
        "pgn_data": str,  # Raw PGN text
        "metadata": dict  # Optional metadata (source platform, etc.)
    }
    
    Returns:
    {
        "success": bool,
        "games_processed": int,
        "message": str
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        pgn_data = data.get('pgn_data')
        
        if not user_id or not pgn_data:
            return jsonify({"error": "Missing user_id or pgn_data"}), 400
        
        # TODO: Implement PGN processing pipeline
        # 1. Clean PGN data
        # 2. Convert to board states
        # 3. Store in MongoDB
        
        return jsonify({
            "success": True,
            "games_processed": 0,
            "message": "PGN upload endpoint - implementation pending"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
