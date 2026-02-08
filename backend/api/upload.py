# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for uploading chess game data
# Handles PGN file uploads and external platform imports (Chess.com, Lichess)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage
import os
import sys

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from data.PGN_cleaner import clean_pgn, validate_pgn_format, split_multiple_games
from data.PGN_to_board_state import pgn_to_board_states
from data.database_manager import DatabaseManager
from data.pgn_downloader import PGNDownloader

upload_bp = Blueprint('upload', __name__)

# Initialize database manager and downloader
db = DatabaseManager()
downloader = PGNDownloader()

@upload_bp.route('/pgn', methods=['POST'])
@jwt_required()
def upload_pgn():
    """
    Upload PGN file or raw PGN text
    
    Request body (form-data):
        file: PGN file upload (optional)
        pgn_text: Raw PGN text (optional, used if no file)
        metadata: JSON string with optional metadata
    
    Returns:
        200: {
            "success": true,
            "games_processed": int,
            "games_stored": int,
            "errors": [str] (if any games failed)
        }
        
        400: {"error": str} - Validation error
        401: {"error": str} - Unauthorized
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Get PGN data from file or text
        pgn_data = None
        
        # Check for file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "Empty filename"}), 400
            
            if not file.filename.endswith('.pgn'):
                return jsonify({"error": "File must be .pgn format"}), 400
            
            pgn_data = file.read().decode('utf-8')
        
        # Check for raw PGN text
        elif 'pgn_text' in request.form:
            pgn_data = request.form['pgn_text']
        
        else:
            return jsonify({"error": "Must provide either 'file' or 'pgn_text'"}), 400
        
        if not pgn_data or not pgn_data.strip():
            return jsonify({"error": "PGN data is empty"}), 400
        
        # Validate PGN format
        if not validate_pgn_format(pgn_data):
            return jsonify({"error": "Invalid PGN format"}), 400
        
        # Split into individual games
        individual_games = split_multiple_games(pgn_data)
        
        if not individual_games:
            return jsonify({"error": "No valid games found in PGN data"}), 400
        
        print(f"📥 Processing {len(individual_games)} game(s) for user {user_id}")
        
        # Process each game
        games_stored = 0
        errors = []
        
        for idx, game_pgn in enumerate(individual_games, 1):
            try:
                # Clean PGN
                cleaned_pgn = clean_pgn(game_pgn)
                
                # Convert to board states with Stockfish evaluations
                result = pgn_to_board_states(cleaned_pgn)
                
                if not result['success']:
                    errors.append(f"Game {idx}: {result.get('error', 'Unknown error')}")
                    continue
                
                # Store in database
                game_id = db.insert_game_data(
                    user_id=user_id,
                    game_metadata=result['metadata'],
                    board_states=result['board_states']
                )
                
                if game_id:
                    games_stored += 1
                else:
                    errors.append(f"Game {idx}: Database storage failed")
                
            except Exception as e:
                errors.append(f"Game {idx}: {str(e)}")
                print(f"❌ Error processing game {idx}: {e}")
        
        print(f"✅ Stored {games_stored}/{len(individual_games)} games for user {user_id}")
        
        response_data = {
            "success": True,
            "games_processed": len(individual_games),
            "games_stored": games_stored
        }
        
        if errors:
            response_data["errors"] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@upload_bp.route('/chess-com', methods=['POST'])
@jwt_required()
def import_chess_com():
    """
    Import games from Chess.com account
    
    Request body:
        {
            "username": str (required),
            "months": [str] (optional, format: "YYYY/MM", default: last 6 months),
            "max_games": int (optional, default: 100)
        }
    
    Returns:
        200: {
            "success": true,
            "games_downloaded": int,
            "games_stored": int,
            "errors": [str] (if any)
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
        
        username = data.get('username', '').strip()
        months = data.get('months')
        max_games = data.get('max_games', 100)
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        if max_games > 500:
            return jsonify({"error": "max_games cannot exceed 500"}), 400
        
        print(f"📥 Importing Chess.com games for {username}")
        
        # Download games from Chess.com
        games_pgn = downloader.download_games(
            platform='chess.com',
            username=username,
            months=months,
            max_games=max_games
        )
        
        if not games_pgn:
            return jsonify({
                "success": False,
                "error": "No games found or failed to download"
            }), 404
        
        # Split into individual games
        individual_games = split_multiple_games(games_pgn)
        
        print(f"📥 Processing {len(individual_games)} Chess.com game(s)")
        
        # Process and store each game
        games_stored = 0
        errors = []
        
        for idx, game_pgn in enumerate(individual_games, 1):
            try:
                cleaned_pgn = clean_pgn(game_pgn)
                result = pgn_to_board_states(cleaned_pgn)
                
                if not result['success']:
                    errors.append(f"Game {idx}: {result.get('error', 'Parse error')}")
                    continue
                
                game_id = db.insert_game_data(
                    user_id=user_id,
                    game_metadata={**result['metadata'], 'source': 'chess.com'},
                    board_states=result['board_states']
                )
                
                if game_id:
                    games_stored += 1
                else:
                    errors.append(f"Game {idx}: Database storage failed")
                    
            except Exception as e:
                errors.append(f"Game {idx}: {str(e)}")
        
        print(f"✅ Stored {games_stored}/{len(individual_games)} Chess.com games")
        
        response_data = {
            "success": True,
            "games_downloaded": len(individual_games),
            "games_stored": games_stored
        }
        
        if errors:
            response_data["errors"] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Chess.com import error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@upload_bp.route('/lichess', methods=['POST'])
@jwt_required()
def import_lichess():
    """
    Import games from Lichess account
    
    Request body:
        {
            "username": str (required),
            "max_games": int (optional, default: 100)
        }
    
    Returns:
        200: {
            "success": true,
            "games_downloaded": int,
            "games_stored": int,
            "errors": [str] (if any)
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
        
        username = data.get('username', '').strip()
        max_games = data.get('max_games', 100)
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        if max_games > 500:
            return jsonify({"error": "max_games cannot exceed 500"}), 400
        
        print(f"📥 Importing Lichess games for {username}")
        
        # Download games from Lichess
        games_pgn = downloader.download_games(
            platform='lichess',
            username=username,
            max_games=max_games
        )
        
        if not games_pgn:
            return jsonify({
                "success": False,
                "error": "No games found or failed to download"
            }), 404
        
        # Split into individual games
        individual_games = split_multiple_games(games_pgn)
        
        print(f"📥 Processing {len(individual_games)} Lichess game(s)")
        
        # Process and store each game
        games_stored = 0
        errors = []
        
        for idx, game_pgn in enumerate(individual_games, 1):
            try:
                cleaned_pgn = clean_pgn(game_pgn)
                result = pgn_to_board_states(cleaned_pgn)
                
                if not result['success']:
                    errors.append(f"Game {idx}: {result.get('error', 'Parse error')}")
                    continue
                
                game_id = db.insert_game_data(
                    user_id=user_id,
                    game_metadata={**result['metadata'], 'source': 'lichess'},
                    board_states=result['board_states']
                )
                
                if game_id:
                    games_stored += 1
                else:
                    errors.append(f"Game {idx}: Database storage failed")
                    
            except Exception as e:
                errors.append(f"Game {idx}: {str(e)}")
        
        print(f"✅ Stored {games_stored}/{len(individual_games)} Lichess games")
        
        response_data = {
            "success": True,
            "games_downloaded": len(individual_games),
            "games_stored": games_stored
        }
        
        if errors:
            response_data["errors"] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Lichess import error: {e}")
        return jsonify({"error": "Internal server error"}), 500
