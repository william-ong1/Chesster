# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Sanitizes raw PGN data by removing comments, extraneous text, and validating format
# This is the first step in the data processing pipeline before parsing

import re
from typing import List, Tuple


def clean_pgn(pgn_text: str) -> str:
    """
    Clean and sanitize raw PGN text by removing comments and extraneous content.
    
    This function performs the following operations:
    1. Removes PGN comments enclosed in curly braces {}
    2. Removes variation annotations enclosed in parentheses ()
    3. Removes annotation symbols like !!, !?, ??, etc.
    4. Normalizes whitespace while preserving game structure
    5. Preserves game headers [Key "Value"] and move text
    
    Args:
        pgn_text: Raw PGN string, potentially with comments and variations
        
    Returns:
        Cleaned PGN string ready for parsing
        
    Example:
        Input:  '[Event "Test"] 1. e4 {good move!} e5 2. Nf3'
        Output: '[Event "Test"]\n\n1. e4 e5 2. Nf3'
    """
    if not pgn_text or not pgn_text.strip():
        return ""
    
    # Step 1: Remove comments enclosed in curly braces {}
    # Comments can span multiple lines and contain nested content
    cleaned = re.sub(r'\{[^}]*\}', '', pgn_text)
    
    # Step 2: Remove variation annotations (alternative move sequences)
    # Variations are enclosed in parentheses and can be nested
    # We remove them iteratively to handle nested variations
    while '(' in cleaned:
        # Match innermost parentheses first
        cleaned = re.sub(r'\([^()]*\)', '', cleaned)
    
    # Step 3: Remove annotation symbols
    # Remove chess annotation symbols: !, !!, ?, ??, !?, ?!, ±, ∓, +-, -+, etc.
    annotation_symbols = [r'!!', r'\?!', r'!\?', r'\?\?', r'!', r'\?', 
                         r'\+\-', r'\-\+', r'±', r'∓', r'∞']
    for symbol in annotation_symbols:
        cleaned = re.sub(symbol, '', cleaned)
    
    # Step 4: Remove numeric annotation glyphs (NAGs) like $1, $2, etc.
    cleaned = re.sub(r'\$\d+', '', cleaned)
    
    # Step 5: Normalize whitespace
    # Replace multiple spaces with single space
    cleaned = re.sub(r' +', ' ', cleaned)
    # Replace multiple newlines with double newline (preserves game separation)
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    
    # Step 6: Clean up whitespace around headers and moves
    # Remove trailing spaces on each line
    cleaned = '\n'.join(line.rstrip() for line in cleaned.split('\n'))
    
    # Step 7: Ensure proper spacing between header section and moves
    # Headers should be followed by blank line before moves start
    cleaned = re.sub(r'(\])\s*(\d+\.)', r'\1\n\n\2', cleaned)
    
    return cleaned.strip()


def validate_pgn_format(pgn_text: str) -> Tuple[bool, str]:
    """
    Validate that PGN text has proper format and required elements.
    
    Checks for:
    - Presence of game result (1-0, 0-1, 1/2-1/2, or *)
    - At least one move in algebraic notation
    - Proper header format if headers are present
    
    Args:
        pgn_text: PGN string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if PGN is valid, False otherwise
        - error_message: Description of validation error, empty string if valid
        
    Example:
        >>> validate_pgn_format('[Event "Test"]\n\n1. e4 e5 1-0')
        (True, '')
        >>> validate_pgn_format('invalid content')
        (False, 'No valid game result found')
    """
    if not pgn_text or not pgn_text.strip():
        return False, "Empty PGN text"
    
    # Check 1: Validate header format if headers are present
    # Headers should be in format [Key "Value"]
    headers = re.findall(r'\[([^\]]+)\]', pgn_text)
    for header in headers:
        if '"' not in header:
            return False, f"Invalid header format: [{header}]"
    
    # Check 2: Look for game result
    # Valid results: 1-0 (white wins), 0-1 (black wins), 1/2-1/2 (draw), * (ongoing/unknown)
    result_pattern = r'(1-0|0-1|1/2-1/2|\*)'
    if not re.search(result_pattern, pgn_text):
        return False, "No valid game result found (expected 1-0, 0-1, 1/2-1/2, or *)"
    
    # Check 3: Look for at least one move in algebraic notation
    # Moves follow pattern: number. move (e.g., "1. e4" or "1... e5")
    move_pattern = r'\d+\.\s*[a-zA-Z]'
    if not re.search(move_pattern, pgn_text):
        return False, "No valid chess moves found"
    
    # All checks passed
    return True, ""


def split_multiple_games(pgn_text: str) -> List[str]:
    """
    Split PGN text containing multiple games into individual game strings.
    
    Games are separated by blank lines after the game result.
    Each game consists of headers (optional) followed by moves and result.
    
    Args:
        pgn_text: PGN string potentially containing multiple games
        
    Returns:
        List of individual PGN game strings
        
    Example:
        Input with 2 games returns list of length 2, each containing one game
    """
    if not pgn_text or not pgn_text.strip():
        return []
    
    games = []
    current_game = []
    lines = pgn_text.split('\n')
    
    for line in lines:
        stripped = line.strip()
        
        # If we hit a blank line and have accumulated content, check if it's end of game
        if not stripped and current_game:
            game_text = '\n'.join(current_game)
            # Check if current game has a result (indicating it's complete)
            if re.search(r'(1-0|0-1|1/2-1/2|\*)', game_text):
                games.append(game_text)
                current_game = []
            else:
                # Blank line within a game, preserve it
                current_game.append(line)
        elif stripped:
            current_game.append(line)
    
    # Don't forget the last game if file doesn't end with blank line
    if current_game:
        game_text = '\n'.join(current_game)
        if re.search(r'(1-0|0-1|1/2-1/2|\*)', game_text):
            games.append(game_text)
    
    return games


def clean_pgn_file(pgn_text: str) -> List[str]:
    """
    Main entry point for cleaning PGN data from file uploads.
    
    Handles multiple games in a single file and returns list of cleaned games.
    This is the function that should be called by the upload API.
    
    Args:
        pgn_text: Raw PGN text from file upload
        
    Returns:
        List of cleaned PGN strings, one per game
        
    Example:
        >>> pgn = load_pgn_file('games.pgn')
        >>> cleaned_games = clean_pgn_file(pgn)
        >>> for game in cleaned_games:
        ...     # Process each game
    """
    # Split into individual games
    games = split_multiple_games(pgn_text)
    
    # Clean each game individually
    cleaned_games = []
    for game in games:
        cleaned = clean_pgn(game)
        # Only include games that pass validation
        is_valid, error = validate_pgn_format(cleaned)
        if is_valid:
            cleaned_games.append(cleaned)
        else:
            # Log validation errors (in production, use proper logging)
            print(f"Warning: Skipping invalid game - {error}")
    
    return cleaned_games
