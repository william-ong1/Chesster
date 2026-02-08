# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Test suite for data pipeline components

import pytest
import sys
sys.path.append('..')

from data.pgn_parser import PGNParser
from data.game_validator import GameValidator
from data.move_extractor import MoveExtractor

class TestPGNParser:
    """Tests for PGN parsing functionality"""
    
    def test_parse_single_game(self):
        """Test parsing a single PGN game"""
        pgn_text = """
        [Event "Test Game"]
        [White "Player1"]
        [Black "Player2"]
        [Result "1-0"]
        
        1. e4 e5 2. Nf3 Nc6 1-0
        """
        
        parser = PGNParser()
        games = parser.parse_pgn_string(pgn_text)
        
        assert len(games) == 1
        assert games[0]['metadata']['white'] == 'Player1'
        assert games[0]['metadata']['black'] == 'Player2'
        assert len(games[0]['moves']) > 0
    
    def test_parse_multiple_games(self):
        """Test parsing multiple PGN games"""
        # TODO: Add test for multiple games
        pass

class TestGameValidator:
    """Tests for game validation"""
    
    def test_validate_good_game(self):
        """Test that valid games pass validation"""
        validator = GameValidator(min_elo=1000, min_moves=10)
        
        game = {
            'metadata': {
                'white_elo': '1500',
                'black_elo': '1450',
                'result': '1-0',
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
