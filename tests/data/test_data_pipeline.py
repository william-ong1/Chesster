# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Test suite for data pipeline components

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
sys.path.append('..')

from data.PGN_cleaner import clean_pgn, validate_pgn_format, split_multiple_games
from data.PGN_to_board_state import pgn_to_board_states
from data.database_manager import DatabaseManager
from data.pgn_downloader import PGNDownloader

class TestPGNCleaner:
    """Tests for PGN cleaning functionality"""
    
    def test_validate_valid_pgn(self):
        """Test validating a proper PGN file"""
        valid_pgn = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"""
        
        assert validate_pgn_format(valid_pgn) == True
    
    def test_validate_invalid_pgn(self):
        """Test that invalid PGN is rejected"""
        invalid_pgn = "This is not a PGN file"
        assert validate_pgn_format(invalid_pgn) == False
    
    def test_clean_pgn_removes_comments(self):
        """Test that comments are removed from PGN"""
        pgn_with_comments = """[Event "Test"]
1. e4 {good move} e5 2. Nf3"""
        
        cleaned = clean_pgn(pgn_with_comments)
        assert '{good move}' not in cleaned
    
    def test_split_multiple_games(self):
        """Test splitting a file with multiple games"""
        multi_pgn = """[Event "Game 1"]
[Result "1-0"]
1. e4 e5 1-0

[Event "Game 2"]
[Result "0-1"]
1. d4 d5 0-1"""
        
        games = split_multiple_games(multi_pgn)
        assert len(games) == 2
        assert 'Game 1' in games[0]
        assert 'Game 2' in games[1]

class TestPGNToBoardState:
    """Tests for PGN to board state conversion"""
    
    def test_convert_simple_game(self):
        """Test converting a simple game to board states"""
        simple_pgn = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 1-0"""
        
        result = pgn_to_board_states(simple_pgn)
        
        assert result['success'] == True
        assert 'board_states' in result
        assert len(result['board_states']) > 0
        assert 'metadata' in result
        assert result['metadata']['white'] == 'Player1'
    
    def test_invalid_pgn_returns_error(self):
        """Test that invalid PGN returns error"""
        invalid_pgn = "1. e4 e5 2. Nf9"  # Invalid move
        
        result = pgn_to_board_states(invalid_pgn)
        assert result['success'] == False
        assert 'error' in result

class TestDatabaseManager:
    """Tests for database operations"""
    
    @patch('data.database_manager.MongoClient')
    def test_insert_game_data(self, mock_mongo):
        """Test inserting game data into database"""
        # Mock MongoDB client
        mock_db = MagicMock()
        mock_mongo.return_value = {'chesster': mock_db}
        
        db_manager = DatabaseManager()
        
        game_metadata = {'white': 'Player1', 'black': 'Player2', 'result': '1-0'}
        board_states = [
            {'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1', 
             'move': 'e4', 'evaluation': 0.3}
        ]
        
        game_id = db_manager.insert_game_data('user123', game_metadata, board_states)
        assert game_id is not None
    
    @patch('data.database_manager.MongoClient')
    def test_get_user_games(self, mock_mongo):
        """Test retrieving user's games"""
        mock_db = MagicMock()
        mock_mongo.return_value = {'chesster': mock_db}
        
        db_manager = DatabaseManager()
        games = db_manager.get_user_games('user123', limit=10)
        
        assert isinstance(games, list)

class TestPGNDownloader:
    """Tests for external platform downloaders"""
    
    @patch('requests.get')
    def test_download_chess_com_games(self, mock_get):
        """Test downloading games from Chess.com"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'games': [
                {'pgn': '[Event "Test"]\n1. e4 e5'}
            ]
        }
        mock_get.return_value = mock_response
        
        downloader = PGNDownloader()
        result = downloader.download_chess_com('testuser', months=['2024/01'])
        
        assert result['success'] == True
        assert len(result['games']) > 0
    
    @patch('requests.get')
    def test_download_lichess_games(self, mock_get):
        """Test downloading games from Lichess"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[Event "Test"]\n1. e4 e5'
        mock_get.return_value = mock_response
        
        downloader = PGNDownloader()
        result = downloader.download_lichess('testuser', max_games=10)
        
        assert result['success'] == True
        assert len(result['games']) > 0

                'time_control': '600+0'
            },
            'moves': ['e4'] * 15  # 15 moves
        }
        
        assert validator.validate_game(game) == True
    
    def test_reject_short_game(self):
        """Test that games with too few moves are rejected"""
        validator = GameValidator(min_elo=1000, min_moves=10)
        
        game = {
            'metadata': {
                'white_elo': '1500',
                'black_elo': '1450',
                'result': '1-0'
            },
            'moves': ['e4'] * 5  # Only 5 moves
        }
        
        assert validator.validate_game(game) == False

class TestMoveExtractor:
    """Tests for move extraction"""
    
    def test_extract_from_game(self):
        """Test extracting states from a game"""
        extractor = MoveExtractor()
        
        game = {
            'moves': ['e4', 'e5', 'Nf3', 'Nc6']
        }
        
        states = extractor.extract_states_and_moves(game)
        
        assert len(states) == 4
        assert all('fen' in state for state in states)
        assert all('move_made' in state for state in states)
