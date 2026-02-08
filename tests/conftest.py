# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Pytest configuration and fixtures

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_pgn():
    """Sample PGN game for testing"""
    return """
    [Event "Test Game"]
    [Site "Test"]
    [Date "2026.02.07"]
    [White "TestPlayer1"]
    [Black "TestPlayer2"]
    [Result "1-0"]
    [WhiteElo "1500"]
    [BlackElo "1450"]
    
    1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0
    """

@pytest.fixture
def sample_fen():
    """Sample FEN board state for testing"""
    return "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
