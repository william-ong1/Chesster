# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Parses PGN text to structured game data using python-chess
# Extracts metadata (ELO, time control, results)

import chess.pgn
import io
from typing import List, Dict, Optional

class PGNParser:
    """
    Converts PGN text to structured game data
    """
    
    def __init__(self):
        self.parsed_games = []
        
    def parse_pgn_string(self, pgn_text: str) -> List[Dict]:
        """
        Parse PGN text into structured game objects
        
        Args:
            pgn_text: Raw PGN string (can contain multiple games)
            
        Returns:
            List of game dictionaries with metadata and moves
        """
        games = []
        pgn_io = io.StringIO(pgn_text)
        
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
                
            # Extract metadata
            game_data = {
                "metadata": {
                    "white": game.headers.get("White", "Unknown"),
                    "black": game.headers.get("Black", "Unknown"),
                    "result": game.headers.get("Result", "*"),
                    "date": game.headers.get("Date", "????.??.??"),
                    "white_elo": game.headers.get("WhiteElo"),
                    "black_elo": game.headers.get("BlackElo"),
                    "time_control": game.headers.get("TimeControl"),
                    "event": game.headers.get("Event"),
                },
                "moves": self._extract_moves(game)
            }
            games.append(game_data)
            
        return games
    
    def _extract_moves(self, game: chess.pgn.Game) -> List[str]:
        """
        Extract move sequence from game
        
        Args:
            game: python-chess Game object
            
        Returns:
            List of moves in SAN notation
        """
        moves = []
        board = game.board()
        for move in game.mainline_moves():
            moves.append(board.san(move))
            board.push(move)
        return moves
