# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Downloads chess game history from chess platform APIs
# Supports Chess.com and Lichess with rate limiting and pagination

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

class PGNDownloader:
    """
    Retrieves game history from chess platform APIs
    
    Supports:
    - Chess.com: Official Public API
    - Lichess: Official API
    """
    
    # API endpoints
    CHESS_COM_BASE = "https://api.chess.com/pub"
    LICHESS_BASE = "https://lichess.org/api"
    
    def __init__(self, platform: str = "chess.com"):
        """
        Initialize PGN downloader
        
        Args:
            platform: "chess.com" or "lichess"
        """
        self.platform = platform.lower()
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Chesster Bot (Chess Style Replication)'
        })
        
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
            
        Raises:
            ValueError: If platform is unsupported or username not found
            requests.RequestException: If API request fails
        """
        if self.platform == "chess.com":
            return self._download_chess_com_games(username, max_games)
        elif self.platform == "lichess":
            return self._download_lichess_games(username, max_games)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _download_chess_com_games(
        self,
        username: str,
        max_games: Optional[int] = None
    ) -> List[str]:
        """
        Download games from Chess.com API
        
        Chess.com API structure:
        1. GET /player/{username}/games/archives -> list of monthly archive URLs
        2. GET each archive URL -> PGN games for that month
        """
        try:
            # Get list of monthly archives
            archives_url = f"{self.CHESS_COM_BASE}/player/{username}/games/archives"
            response = self.session.get(archives_url)
            response.raise_for_status()
            
            archives = response.json().get("archives", [])
            
            if not archives:
                print(f"⚠️ No games found for user: {username}")
                return []
            
            # Download games from each archive (newest first)
            pgn_list = []
            total_downloaded = 0
            
            for archive_url in reversed(archives):
                if max_games and total_downloaded >= max_games:
                    break
                
                time.sleep(self.rate_limit_delay)  # Rate limiting
                
                response = self.session.get(archive_url)
                response.raise_for_status()
                
                games_data = response.json().get("games", [])
                
                for game in games_data:
                    if max_games and total_downloaded >= max_games:
                        break
                    
                    pgn = game.get("pgn")
                    if pgn:
                        pgn_list.append(pgn)
                        total_downloaded += 1
                
                print(f"📥 Downloaded {total_downloaded} games so far...")
            
            print(f"✅ Downloaded {total_downloaded} games from Chess.com for {username}")
            return pgn_list
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"User not found: {username}")
            raise
        except Exception as e:
            print(f"❌ Error downloading from Chess.com: {e}")
            raise
    
    def _download_lichess_games(
        self,
        username: str,
        max_games: Optional[int] = None
    ) -> List[str]:
        """
        Download games from Lichess API
        
        Lichess API structure:
        - GET /api/games/user/{username} -> stream of PGN games
        - Supports parameters: max (limit), rated (filter), perfType (variant)
        """
        try:
            url = f"{self.LICHESS_BASE}/games/user/{username}"
            params = {
                "pgnInJson": "false",  # Get raw PGN
                "clocks": "false",  # Exclude clock data
                "evals": "false",  # Exclude evaluations
                "opening": "true"  # Include opening info
            }
            
            if max_games:
                params["max"] = max_games
            
            response = self.session.get(url, params=params, stream=True)
            response.raise_for_status()
            
            # Lichess returns newline-delimited PGN
            pgn_list = []
            current_pgn = []
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    current_pgn.append(line)
                else:
                    # Empty line marks end of game
                    if current_pgn:
                        pgn_list.append("\n".join(current_pgn))
                        current_pgn = []
            
            # Handle last game
            if current_pgn:
                pgn_list.append("\n".join(current_pgn))
            
            print(f"✅ Downloaded {len(pgn_list)} games from Lichess for {username}")
            return pgn_list
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"User not found: {username}")
            raise
        except Exception as e:
            print(f"❌ Error downloading from Lichess: {e}")
            raise
    
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
        if self.platform == "chess.com":
            return self._download_chess_com_by_date(username, year, month)
        elif self.platform == "lichess":
            # Lichess API doesn't support month-specific filtering easily
            # Would need to download all and filter
            print("⚠️ Date-specific download not optimized for Lichess")
            return self._download_lichess_games(username, max_games=None)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _download_chess_com_by_date(
        self,
        username: str,
        year: int,
        month: int
    ) -> List[str]:
        """
        Download Chess.com games for specific month
        
        Chess.com archives are organized by month: YYYY/MM
        """
        try:
            # Format: https://api.chess.com/pub/player/{username}/games/YYYY/MM
            archive_url = f"{self.CHESS_COM_BASE}/player/{username}/games/{year:04d}/{month:02d}"
            
            response = self.session.get(archive_url)
            response.raise_for_status()
            
            games_data = response.json().get("games", [])
            pgn_list = [game.get("pgn") for game in games_data if game.get("pgn")]
            
            print(f"✅ Downloaded {len(pgn_list)} games for {year}-{month:02d}")
            return pgn_list
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"⚠️ No games found for {year}-{month:02d}")
                return []
            raise
        except Exception as e:
            print(f"❌ Error downloading by date: {e}")
            raise
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user profile information
        
        Args:
            username: Platform username
            
        Returns:
            Dictionary with user info or None if not found
        """
        try:
            if self.platform == "chess.com":
                url = f"{self.CHESS_COM_BASE}/player/{username}"
            elif self.platform == "lichess":
                url = f"{self.LICHESS_BASE}/user/{username}"
            else:
                return None
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.HTTPError:
            return None
        except Exception as e:
            print(f"❌ Error fetching user info: {e}")
            return None
    
    def close(self):
        """Close HTTP session"""
        self.session.close()
