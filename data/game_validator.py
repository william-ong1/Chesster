# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Filters low-quality games from dataset
# Removes incomplete games, very low ELO games, and fast time controls

from typing import List, Dict

class GameValidator:
    """
    Filters low-quality chess games from training data
    """
    
    def __init__(
        self,
        min_elo: int = 1000,
        min_moves: int = 10,
        exclude_bullet: bool = True
    ):
        """
        Initialize game validator
        
        Args:
            min_elo: Minimum ELO rating for included games
            min_moves: Minimum number of moves for valid game
            exclude_bullet: Whether to exclude bullet (very fast) games
        """
        self.min_elo = min_elo
        self.min_moves = min_moves
        self.exclude_bullet = exclude_bullet
        
    def validate_game(self, game: Dict) -> bool:
        """
        Check if a game meets quality criteria
        
        Args:
            game: Game dictionary with metadata and moves
            
        Returns:
            True if game is valid, False otherwise
        """
        metadata = game.get("metadata", {})
        moves = game.get("moves", [])
        
        # Check minimum moves
        if len(moves) < self.min_moves:
            return False
        
        # Check if game completed (not abandoned)
        result = metadata.get("result", "*")
        if result == "*":
            return False
        
        # Check ELO ratings
        white_elo = self._parse_elo(metadata.get("white_elo"))
        black_elo = self._parse_elo(metadata.get("black_elo"))
        
        if white_elo and white_elo < self.min_elo:
            return False
        if black_elo and black_elo < self.min_elo:
            return False
        
        # Check time control (exclude bullet if configured)
        if self.exclude_bullet:
            time_control = metadata.get("time_control", "")
            if self._is_bullet_game(time_control):
                return False
        
        return True
    
    def filter_games(self, games: List[Dict]) -> List[Dict]:
        """
        Filter list of games by quality criteria
        
        Args:
            games: List of game dictionaries
            
        Returns:
            Filtered list of valid games
        """
        return [game for game in games if self.validate_game(game)]
    
    def _parse_elo(self, elo_str) -> int:
        """Parse ELO string to integer, handling None and "?" """
        if elo_str is None or elo_str == "?":
            return None
        try:
            return int(elo_str)
        except (ValueError, TypeError):
            return None
    
    def _is_bullet_game(self, time_control: str) -> bool:
        """
        Check if game is bullet time control (< 180 seconds)
        
        Args:
            time_control: Time control string (e.g., "60+0", "180+2")
            
        Returns:
            True if bullet game
        """
        if not time_control or time_control == "-":
            return False
        
        try:
            # Parse format like "180+2" (base time + increment)
            base_time = int(time_control.split('+')[0])
            return base_time < 180
        except (ValueError, IndexError):
            return False
