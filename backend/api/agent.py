# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for chess agent gameplay
# Handles move generation and position evaluation using trained models

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import chess
import time
import os
import sys

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from ML.agent import Agent
from ML.model_cache import ModelCache
from data.database_manager import DatabaseManager

agent_bp = Blueprint('agent', __name__)

# Initialize database manager and model cache
db = DatabaseManager()
model_cache = ModelCache(max_size=5)

@agent_bp.route('/move', methods=['POST'])
@jwt_required()
def get_move():
    """
    Get the bot's next move for a given board state
    
    Request body:
        {
            "fen": str (required),
            "model_id": str (optional, uses active model if not provided),
            "depth": int (optional, default: 3, max: 6)
        }
    
    Returns:
        200: {
            "move": str (UCI format, e.g., "e2e4"),
            "move_san": str (SAN format, e.g., "e4"),
            "evaluation": float,
            "thinking_time": float,
            "model_id": str,
            "depth": int
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
        
        fen = data.get('fen', '').strip()
        model_id = data.get('model_id')
        depth = data.get('depth', 3)
        
        # Validation
        if not fen:
            return jsonify({"error": "fen is required"}), 400
        
        if depth < 1 or depth > 6:
            return jsonify({"error": "depth must be between 1 and 6"}), 400
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400
        
        # Check if game is over
        if board.is_game_over():
            return jsonify({"error": "Game is already over"}), 400
        
        # Get model_id (use provided or get active model)
        if not model_id:
            model_id = db.get_active_model_id(user_id)
            if not model_id:
                return jsonify({
                    "error": "No active model found. Train a model first."
                }), 404
        
        # Load model
        model_data = model_cache.get(model_id)
        if not model_data:
            return jsonify({"error": "Failed to load model"}), 500
        
        # Initialize agent with loaded model
        agent = Agent(
            model=model_data['model'],
            depth=depth
        )
        
        # Generate move
        start_time = time.time()
        move, evaluation = agent.get_move(board)
        thinking_time = time.time() - start_time
        
        if not move:
            return jsonify({"error": "Failed to generate move"}), 500
        
        # Convert to SAN notation for readability
        move_san = board.san(move)
        
        print(f"🤖 Agent move: {move_san} (eval: {evaluation:.3f}, time: {thinking_time:.3f}s)")
        
        return jsonify({
            "move": move.uci(),
            "move_san": move_san,
            "evaluation": evaluation,
            "thinking_time": thinking_time,
            "model_id": model_id,
            "depth": depth
        }), 200
        
    except Exception as e:
        print(f"❌ Get move error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@agent_bp.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate_position():
    """
    Evaluate a chess position without making a move
    
    Request body:
        {
            "fen": str (required),
            "model_id": str (optional, uses active model if not provided)
        }
    
    Returns:
        200: {
            "evaluation": float,
            "model_id": str,
            "fen": str,
            "turn": str (white/black),
            "legal_moves": int
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
        
        fen = data.get('fen', '').strip()
        model_id = data.get('model_id')
        
        # Validation
        if not fen:
            return jsonify({"error": "fen is required"}), 400
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400
        
        # Get model_id (use provided or get active model)
        if not model_id:
            model_id = db.get_active_model_id(user_id)
            if not model_id:
                return jsonify({
                    "error": "No active model found. Train a model first."
                }), 404
        
        # Load model
        model_data = model_cache.get(model_id)
        if not model_data:
            return jsonify({"error": "Failed to load model"}), 500
        
        # Initialize agent with loaded model
        agent = Agent(
            model=model_data['model'],
            depth=1  # Depth 1 for quick evaluation
        )
        
        # Evaluate position
        evaluation = agent._evaluate_position(board)
        
        # Get board info
        turn = "white" if board.turn == chess.WHITE else "black"
        legal_moves = list(board.legal_moves)
        
        print(f"📊 Position evaluation: {evaluation:.3f} ({turn} to move)")
        
        return jsonify({
            "evaluation": evaluation,
            "model_id": model_id,
            "fen": fen,
            "turn": turn,
            "legal_moves": len(legal_moves)
        }), 200
        
    except Exception as e:
        print(f"❌ Evaluate position error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@agent_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_game():
    """
    Analyze multiple positions (e.g., full game analysis)
    
    Request body:
        {
            "fens": [str] (required, list of FEN positions),
            "model_id": str (optional, uses active model if not provided)
        }
    
    Returns:
        200: {
            "analysis": [{
                "fen": str,
                "evaluation": float,
                "move_number": int
            }],
            "model_id": str,
            "positions_analyzed": int
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
        
        fens = data.get('fens', [])
        model_id = data.get('model_id')
        
        # Validation
        if not fens or not isinstance(fens, list):
            return jsonify({"error": "fens must be a non-empty list"}), 400
        
        if len(fens) > 200:
            return jsonify({"error": "Maximum 200 positions per request"}), 400
        
        # Get model_id (use provided or get active model)
        if not model_id:
            model_id = db.get_active_model_id(user_id)
            if not model_id:
                return jsonify({
                    "error": "No active model found. Train a model first."
                }), 404
        
        # Load model
        model_data = model_cache.get(model_id)
        if not model_data:
            return jsonify({"error": "Failed to load model"}), 500
        
        # Initialize agent with loaded model
        agent = Agent(
            model=model_data['model'],
            depth=1  # Depth 1 for quick batch analysis
        )
        
        # Analyze each position
        analysis = []
        for idx, fen in enumerate(fens, 1):
            try:
                board = chess.Board(fen)
                evaluation = agent._evaluate_position(board)
                
                analysis.append({
                    "fen": fen,
                    "evaluation": evaluation,
                    "move_number": idx
                })
            except ValueError as e:
                analysis.append({
                    "fen": fen,
                    "error": f"Invalid FEN: {str(e)}",
                    "move_number": idx
                })
        
        print(f"📈 Analyzed {len(analysis)} positions")
        
        return jsonify({
            "analysis": analysis,
            "model_id": model_id,
            "positions_analyzed": len(analysis)
        }), 200
        
    except Exception as e:
        print(f"❌ Analyze game error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@agent_bp.route('/make-move', methods=['POST'])
@jwt_required()
def make_move():
    """
    Validate and execute a player's move, returning the new board state
    
    Request body:
        {
            "fen": str (required, current position),
            "move": str (required, move in UCI format, e.g., "e2e4" or SAN format "e4"),
            "promotion": str (optional, piece to promote to: q/r/b/n, default: q)
        }
    
    Returns:
        200: {
            "new_fen": str (position after the move),
            "move_san": str (move in SAN notation),
            "move_uci": str (move in UCI notation),
            "is_game_over": bool,
            "game_result": str (optional, "1-0", "0-1", "1/2-1/2"),
            "is_checkmate": bool,
            "is_stalemate": bool,
            "is_check": bool
        }
        
        400: {"error": str} - Validation or illegal move error
        401: {"error": str} - Unauthorized
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        fen = data.get('fen', '').strip()
        move_str = data.get('move', '').strip()
        promotion = data.get('promotion', 'q')
        
        # Validation
        if not fen:
            return jsonify({"error": "fen is required"}), 400
        
        if not move_str:
            return jsonify({"error": "move is required"}), 400
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400
        
        # Check if game is already over
        if board.is_game_over():
            return jsonify({"error": "Game is already over"}), 400
        
        # Try to parse and execute the move
        try:
            # Try UCI format first (e.g., "e2e4", "e7e8q")
            move = chess.Move.from_uci(move_str)
            if move not in board.legal_moves:
                raise ValueError("Illegal move")
        except:
            # Try SAN format (e.g., "e4", "Nf3", "O-O")
            try:
                move = board.parse_san(move_str)
            except:
                return jsonify({"error": f"Invalid or illegal move: {move_str}"}), 400
        
        # Store SAN and UCI before making move
        move_san = board.san(move)
        move_uci = move.uci()
        
        # Execute the move
        board.push(move)
        
        # Get new position and game state
        new_fen = board.fen()
        is_game_over = board.is_game_over()
        is_checkmate = board.is_checkmate()
        is_stalemate = board.is_stalemate()
        is_check = board.is_check()
        
        # Determine game result
        game_result = None
        if is_game_over:
            if is_checkmate:
                # Winner is the player who just moved
                game_result = "1-0" if board.turn == chess.BLACK else "0-1"
            elif is_stalemate or board.is_insufficient_material() or \
                 board.is_seventyfive_moves() or board.is_fivefold_repetition():
                game_result = "1/2-1/2"
        
        print(f"✅ Move executed: {move_san} ({move_uci})")
        
        return jsonify({
            "new_fen": new_fen,
            "move_san": move_san,
            "move_uci": move_uci,
            "is_game_over": is_game_over,
            "game_result": game_result,
            "is_checkmate": is_checkmate,
            "is_stalemate": is_stalemate,
            "is_check": is_check
        }), 200
        
    except Exception as e:
        print(f"❌ Make move error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@agent_bp.route('/legal-moves', methods=['POST'])
@jwt_required()
def get_legal_moves():
    """
    Get all legal moves for a given position
    
    Request body:
        {
            "fen": str (required),
            "square": str (optional, e.g., "e2" - get moves for specific piece)
        }
    
    Returns:
        200: {
            "legal_moves": [str] (UCI format),
            "legal_moves_san": [str] (SAN format),
            "count": int,
            "fen": str
        }
        
        400: {"error": str} - Validation error
        401: {"error": str} - Unauthorized
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        fen = data.get('fen', '').strip()
        square_str = data.get('square', '').strip()
        
        # Validation
        if not fen:
            return jsonify({"error": "fen is required"}), 400
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError as e:
            return jsonify({"error": f"Invalid FEN string: {str(e)}"}), 400
        
        # Get legal moves
        if square_str:
            # Get moves for specific square
            try:
                square = chess.parse_square(square_str)
                legal_moves = [move for move in board.legal_moves if move.from_square == square]
            except ValueError:
                return jsonify({"error": f"Invalid square: {square_str}"}), 400
        else:
            # Get all legal moves
            legal_moves = list(board.legal_moves)
        
        # Convert to both UCI and SAN
        legal_moves_uci = [move.uci() for move in legal_moves]
        legal_moves_san = [board.san(move) for move in legal_moves]
        
        return jsonify({
            "legal_moves": legal_moves_uci,
            "legal_moves_san": legal_moves_san,
            "count": len(legal_moves),
            "fen": fen
        }), 200
        
    except Exception as e:
        print(f"❌ Get legal moves error: {e}")
        return jsonify({"error": "Internal server error"}), 500
