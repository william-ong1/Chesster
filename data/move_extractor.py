# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Extracts board states (FEN) and corresponding moves from games
# Traverses game move-by-move to build training data

import chess
from typing import List, Dict, Tuple

class MoveExtractor:
    """
    Extracts board states and moves from parsed games
    """
    
    def __init__(self):
        pass
    
    def extract_states_and_moves(self, game: Dict) -> List[Dict]:
        """
        Extract all board states and moves from a game
        
        Args:
            game: Game dictionary with metadata and moves list
            
        Returns:
            List of {fen, move_made, move_number} dictionaries
        """
        board = chess.Board()
        states = []
        moves = game.get("moves", [])
        
        for move_number, move_san in enumerate(moves, start=1):
            try:
                # Record current state before move
                fen = board.fen()
                
                # Parse and make the move
                move = board.parse_san(move_san)
                board.push(move)
                
                # Store state with move that was made
                states.append({
                    "fen": fen,
                    "move_made": move_san,
                    "move_number": move_number,
                    "move_uci": move.uci()  # Also store UCI format
                })
                
            except (ValueError, chess.IllegalMoveError) as e:
                # Skip invalid moves
                print(f"Warning: Invalid move '{move_san}' at position {move_number}: {e}")
                break
        
        return states
    
    def extract_from_multiple_games(self, games: List[Dict]) -> List[Dict]:
        """
        Extract states from multiple games
        
        Args:
            games: List of game dictionaries
            
        Returns:
            Flat list of all states from all games
        """
        all_states = []
        for game in games:
            states = self.extract_states_and_moves(game)
            # Add game metadata to each state
            for state in states:
                state["game_metadata"] = game.get("metadata", {})
            all_states.extend(states)
        
        return all_states
