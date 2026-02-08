# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Downloads chess game history from chess platform APIs
# Supports Chess.com and Lichess with rate limiting and pagination

import requests
import time
from typing import List, Dict, Optional

class PGNDownloader:
    """
    Retrieves game history from chess platform APIs
    """
    
    def __init__(self, platform: str = "chess.com"):
        """
        Initialize PGN downloader
        
        Args:
            platform: "chess.com" or "lichess"
        """
        self.platform = platform.lower()
        self.rate_limit_delay = 1.0  # Seconds between requests
        
    def download_user_games(
        self, 
        username: str, 
        max_games: Optional[int] = None
    ) -> List[str]:
        """
        Download all games for a user from the platform
        
        Args:
            username: Platform username
            max_games: Maximum number of games to download (None for all)
            
        Returns:
            List of PGN strings
        """
        # TODO: Implement platform-specific API calls
        # Chess.com API: https://api.chess.com/pub/player/{username}/games/archives
        # Lichess API: https://lichess.org/api/games/user/{username}
        pass
    
    def download_games_by_date(
        self,
        username: str,
        year: int,
        month: int
    ) -> List[str]:
        """
        Download games for a specific month
        
        Args:
            username: Platform username
            year: Year (e.g., 2026)
            month: Month (1-12)
            
        Returns:
            List of PGN strings
        """
        # TODO: Implement date-specific download
        pass
