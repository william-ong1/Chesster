# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for chess agent gameplay
# POST /api/get-move - Get bot's move for a given board state

from flask import Blueprint, request, jsonify
import chess
import sys
sys.path.append('../ML')

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/get-move', methods=['POST'])
def get_move():
    """
    Get the bot's move for a given board state
    
    Request body:
    {
        "user_id": str,
        "fen": str,  # Current board state in FEN notation
        "model_id": str  # Optional - use specific model version
    }
    
    Returns:
    {
        "move": str,  # Move in SAN notation (e.g., "Nf3", "e4")
        "evaluation": float,  # Position evaluation score
        "thinking_time": float  # Time taken in seconds
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        fen = data.get('fen')
        model_id = data.get('model_id')
        
        if not user_id or not fen:
            return jsonify({"error": "Missing user_id or fen"}), 400
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError:
            return jsonify({"error": "Invalid FEN string"}), 400
        
        # TODO: Implement agent move generation
        # 1. Load model for user (or use model_id)
        # 2. Generate move using Agent class
        # 3. Return move in SAN notation
        
        return jsonify({
            "move": "e4",
            "evaluation": 0.2,
            "thinking_time": 0.5,
            "message": "Agent endpoint - implementation pending"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
