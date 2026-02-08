# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Takes in a PGN string with a game and returns a list of board states making up the game.
# The output should be a list of board states, each board state being a FEN string.
# Example of a board state: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

import chess.pgn
import io
from typing import List, Optional


def pgn_to_board_states(pgn_string: str) -> List[str]:
    """
    Convert a PGN string to a list of FEN board states.
    
    This function parses a single PGN game and generates the FEN notation
    for each position in the game, from the starting position through all moves.
    This is the main function specified in the planning document for converting
    PGN notation to board states for ML training.
    
    Args:
        pgn_string: A single PGN game string (cleaned, without comments)
        
    Returns:
        List of FEN strings, one for each position in the game
        Returns empty list if PGN cannot be parsed
        
    Example:
        >>> pgn = '[Event "Test"]\n\n1. e4 e5 2. Nf3 1-0'
        >>> states = pgn_to_board_states(pgn)
        >>> len(states)  # Starting position + 3 moves
        4
        >>> states[0]  # Starting position
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    """
    # Validate input
    if not pgn_string or not pgn_string.strip():
        return []
    
    try:
        # Parse PGN using python-chess library
        # StringIO allows us to treat string as file-like object for parser
        pgn_io = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn_io)
        
        if game is None:
            # Unable to parse game - invalid PGN format
            return []
        
        # Initialize board at starting position
        board = game.board()
        board_states = []
        
        # Capture starting position FEN
        board_states.append(board.fen())
        
        # Iterate through all moves in the game
        # mainline_moves() gives us the primary line (no variations)
        for move in game.mainline_moves():
            # Apply move to board
            board.push(move)
            # Capture FEN after this move
            board_states.append(board.fen())
        
        return board_states
        
    except Exception as e:
        # Log error in production - for now print to console
        print(f"Error parsing PGN: {e}")
        return []


def pgn_string_to_fen_list(pgn_string: str) -> List[str]:
    """
    Alias for pgn_to_board_states() for backwards compatibility.
    
    Some parts of the codebase may expect this function name.
    
    Args:
        pgn_string: A single PGN game string
        
    Returns:
        List of FEN strings representing board states
    """
    return pgn_to_board_states(pgn_string)


def multiple_pgn_to_board_states(pgn_strings: List[str]) -> List[List[str]]:
    """
    Convert multiple PGN games to lists of board states.
    
    Useful when processing a file with multiple games.
    Each game produces its own list of FEN states.
    
    Args:
        pgn_strings: List of PGN game strings
        
    Returns:
        List of lists - each inner list contains FEN states for one game
        
    Example:
        >>> games = ['[Event "Game1"]\n\n1. e4 e5 1-0', 
        ...          '[Event "Game2"]\n\n1. d4 d5 1-0']
        >>> all_states = multiple_pgn_to_board_states(games)
        >>> len(all_states)  # 2 games
        2
        >>> len(all_states[0])  # FEN states for game 1
        3
    """
    all_board_states = []
    
    for pgn_string in pgn_strings:
        states = pgn_to_board_states(pgn_string)
        if states:  # Only include games that parsed successfully
            all_board_states.append(states)
    
    return all_board_states


def get_final_position(pgn_string: str) -> Optional[str]:
    """
    Get only the final board state FEN from a PGN game.
    
    Useful for analyzing game endings without processing all intermediate positions.
    
    Args:
        pgn_string: A single PGN game string
        
    Returns:
        FEN string of final position, or None if parsing failed
        
    Example:
        >>> pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0'
        >>> final_fen = get_final_position(pgn)
        >>> final_fen is not None
        True
    """
    states = pgn_to_board_states(pgn_string)
    return states[-1] if states else None


def get_position_at_move(pgn_string: str, move_number: int) -> Optional[str]:
    """
    Get the board state FEN after a specific move number.
    
    Args:
        pgn_string: A single PGN game string
        move_number: Which move position to return (0 = starting position)
        
    Returns:
        FEN string at that move, or None if move_number is out of range
        
    Example:
        >>> pgn = '1. e4 e5 2. Nf3 1-0'
        >>> get_position_at_move(pgn, 0)  # Starting position
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        >>> get_position_at_move(pgn, 2)  # After 1. e4 e5
        '...'
    """
    states = pgn_to_board_states(pgn_string)
    
    if not states or move_number < 0 or move_number >= len(states):
        return None
    
    return states[move_number]
