# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for chess agent gameplay
# Handles move generation and position evaluation using trained models

import chess
import os
import sys
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ML.agent import Agent

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/get-move", methods=["POST"])
@jwt_required()
def get_move():
    """
    Get the bot's next move for a given board state

    Request body:
        {
            "fen": str (required),
            "model_id": str (optional, uses active model if not provided),
        }

    Returns:
        200: {
            "move": str (UCI format, e.g., "e2e4"),
            "move_san": str (SAN format, e.g., "e4"),
        }

        400: {"error": str} - Validation error
        401: {"error": str} - Unauthorized
        404: {"error": str} - No model found
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()

        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        fen = data.get("fen", "").strip()
        model_id = data.get("model_id")

        # Validation
        if not fen:
            return jsonify({"error": "fen is required"}), 400

        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400

        if board.is_game_over():
            return jsonify({"error": "Game is already over"}), 400

        if not model_id:
            model_id = db.get_active_model_id(user_id)
            if not model_id:
                return (
                    jsonify({"error": "No active model found. Train a model first."}),
                    404,
                )

        model_data = model_cache.get(model_id)
        if not model_data:
            return jsonify({"error": "Failed to load model"}), 500

        agent = Agent(model=model_data["model"])

        move = agent.get_move(board)

        if not move:
            return jsonify({"error": "Failed to generate move"}), 500

        move_san = board.san(move)

        return (
            jsonify(
                {
                    "move": move.uci(),
                    "move_san": move_san,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"❌ Get move error: {e}")
        return jsonify({"error": "Internal server error"}), 500
