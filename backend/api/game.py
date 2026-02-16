# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for chess agent gameplay
# Handles move generation and position evaluation using trained models

import chess
import os
import sys
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

game_bp = Blueprint("game", __name__)


@game_bp.route("/make-move", methods=["POST"])
@jwt_required()
def make_move():
    """
    Validate and execute a chess move (UCI format only).

    Request body:
        {
            "fen": str (required),
            "move": str (required, UCI format, e.g., "e2e4", "e7e8q")
        }

    Returns:
        200: {
            "new_fen": str,
            "move_san": str,
            "move_uci": str,
            "is_game_over": bool,
            "is_checkmate": bool,
            "is_stalemate": bool,
            "is_check": bool,
            "game_result": str | null
        }

        400: {"error": str}
        401: {"error": str}
        500: {"error": str}
    """
    try:
        get_jwt_identity()  # Validate JWT

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        fen = data.get("fen", "").strip()
        move_str = data.get("move", "").strip()

        if not fen:
            return jsonify({"error": "fen is required"}), 400

        if not move_str:
            return jsonify({"error": "move is required"}), 400

        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400

        if board.is_game_over():
            return jsonify({"error": "Game is already over"}), 400

        try:
            move = chess.Move.from_uci(move_str)
        except ValueError:
            return jsonify({"error": f"Invalid UCI move format: {move_str}"}), 400

        if move not in board.legal_moves:
            return jsonify({"error": "Illegal move"}), 400

        move_san = board.san(move)
        move_uci = move.uci()

        board.push(move)

        new_fen = board.fen()

        is_game_over = board.is_game_over()
        is_checkmate = board.is_checkmate()
        is_stalemate = board.is_stalemate()
        is_check = board.is_check()

        return (
            jsonify(
                {
                    "new_fen": new_fen,
                    "move_san": move_san,
                    "move_uci": move_uci,
                    "is_game_over": is_game_over,
                    "is_checkmate": is_checkmate,
                    "is_stalemate": is_stalemate,
                    "is_check": is_check,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"❌ Make move error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@game_bp.route("/positions/legal-moves", methods=["POST"])
@jwt_required()
def get_legal_moves():
    """
    Get all legal moves for the side to move in a given FEN position.

    Request body:
        {
            "fen": str (required)
        }

    Returns:
        200: {
            "moves": [
                {
                    "uci": str,
                    "san": str,
                    "from": str,
                    "to": str,
                    "promotion": str | null
                }
            ]
        }

        400: {"error": str}
        401: {"error": str}
        500: {"error": str}
    """
    try:
        get_jwt_identity()  # Ensure JWT is valid

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        fen = data.get("fen", "").strip()
        if not fen:
            return jsonify({"error": "fen is required"}), 400

        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400

        moves = []

        for move in board.legal_moves:
            moves.append(
                {
                    "uci": move.uci(),
                    "san": board.san(move),
                    "from": chess.square_name(move.from_square),
                    "to": chess.square_name(move.to_square),
                    "promotion": (
                        chess.piece_symbol(move.promotion) if move.promotion else None
                    ),
                }
            )

        return jsonify({"moves": moves}), 200

    except Exception as e:
        print(f"❌ Get legal moves error: {e}")
        return jsonify({"error": "Internal server error"}), 500
