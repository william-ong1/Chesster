# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for chess agent gameplay
# Handles move generation for chess bot

import chess
import os
import sys
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ML.agent import Agent

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/make-move", methods=["POST"])
@jwt_required()
def make_move():
    """
    Takes a player move and saves it
    Gets the bot's move, makes it, and saves it
    Return the next board state

    Request body:
        {
            "fen": str (required),
            "move": str (required, UCI format, e.g., "e2e4", "e7e8q")
        }

    Returns:
        200: {
            "new_fen": str,
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
            player_move = chess.Move.from_uci(move_str)
        except ValueError:
            return (
                jsonify({"error": f"Invalid UCI move format: {move_str}"}),
                400,
            )

        # TODO save the player move to database

        agent = Agent(
            "model_id"
        )  # TODO update this to retreive model from database
        agent_move = agent.get_move(board)

        # save the agent move to database
        board.push(agent_move)

        new_fen = board.fen()

        is_game_over = board.is_game_over()
        is_checkmate = board.is_checkmate()
        is_stalemate = board.is_stalemate()
        is_check = board.is_check()

        return (
            jsonify(
                {
                    "new_fen": new_fen,
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
