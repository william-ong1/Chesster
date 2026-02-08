# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Chess dataset class for PyTorch DataLoader
# Loads board states and target scores from MongoDB for training

import torch
from torch.utils.data import Dataset
from typing import List, Dict, Optional
from pymongo import MongoClient
import os
import chess
import chess.engine

class ChessDataset(Dataset):
    """
    PyTorch Dataset for chess training data
    
    This dataset is designed for training evaluation networks that output
    position scores (not policy networks that output moves). Each example
    consists of a board state tensor and a target score computed from:
    1. Player move frequency (did the player make this move from this position?)
    2. Stockfish evaluation (what's the objective quality of this position?)
    
    The weighted combination teaches the model to replicate the player's style
    while maintaining chess understanding.
    """
    
    def __init__(
        self,
        user_id: str,
        encoder,
        stockfish_path: Optional[str] = None,
        player_weight: float = 0.7,
        engine_weight: float = 0.3,
        train: bool = True,
        train_split: float = 0.8
    ):
        """
        Initialize dataset
        
        Args:
            user_id: MongoDB user ID to load games for
            encoder: StateEncoder instance for converting FEN to tensors
            stockfish_path: Path to Stockfish binary (uses STOCKFISH_PATH env if None)
            player_weight: Weight for player move influence (0-1)
            engine_weight: Weight for engine evaluation influence (0-1)
            train: If True, use training split; if False, use validation split
            train_split: Fraction of data to use for training (rest is validation)
        """
        self.user_id = user_id
        self.encoder = encoder
        self.player_weight = player_weight
        self.engine_weight = engine_weight
        self.train = train
        self.train_split = train_split
        
        # Initialize Stockfish engine
        stockfish_path = stockfish_path or os.getenv("STOCKFISH_PATH", "/usr/local/bin/stockfish")
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            self.engine.configure({"Threads": 1, "Hash": 128})
        except Exception as e:
            print(f"Warning: Could not initialize Stockfish at {stockfish_path}: {e}")
            print("Falling back to player-only scoring (no engine evaluation)")
            self.engine = None
        
        # Load game data from MongoDB
        self.states = self._load_game_data()
        
        # Split into train/validation
        split_idx = int(len(self.states) * train_split)
        if train:
            self.states = self.states[:split_idx]
        else:
            self.states = self.states[split_idx:]
        
        # Precompute target scores
        self._compute_target_scores()
    
    def _load_game_data(self) -> List[Dict]:
        """
        Load game states from MongoDB
        
        Returns:
            List of state dictionaries with {fen, move_made, move_number, game_id}
        """
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri)
        db = client.chesster
        
        # Query all games for this user
        user_games = db.game_data.find({"user_id": self.user_id})
        
        states = []
        for game_doc in user_games:
            for game in game_doc.get("games", []):
                game_id = game.get("game_id")
                for state in game.get("states", []):
                    states.append({
                        "fen": state["fen"],
                        "move_made": state["move_made"],
                        "move_number": state["move_number"],
                        "game_id": game_id
                    })
        
        client.close()
        
        if not states:
            raise ValueError(f"No game data found for user_id: {self.user_id}")
        
        return states
    
    def _compute_target_scores(self):
        """
        Compute target scores for each position using weighted combination
        of player behavior and engine evaluation
        """
        for state in self.states:
            # Player score: 1.0 if player made this move, 0.0 otherwise
            # (In practice, this is always 1.0 since we only store positions
            # where the player made a move, but included for clarity)
            player_score = 1.0
            
            # Engine score: Stockfish evaluation in centipawns, normalized
            if self.engine is not None:
                try:
                    board = chess.Board(state["fen"])
                    info = self.engine.analyse(board, chess.engine.Limit(depth=15))
                    
                    # Get score from white's perspective
                    score = info["score"].white()
                    
                    # Convert to float (centipawns or mate score)
                    if score.is_mate():
                        # Mate scores: convert to large positive/negative values
                        mate_in = score.mate()
                        engine_score = 10.0 if mate_in > 0 else -10.0
                    else:
                        # Centipawn scores: normalize to roughly [-1, 1] range
                        centipawns = score.score()
                        engine_score = centipawns / 100.0  # Divide by 100 for pawn units
                        engine_score = max(-10.0, min(10.0, engine_score))  # Clamp
                except Exception as e:
                    print(f"Warning: Stockfish evaluation failed for {state['fen']}: {e}")
                    engine_score = 0.0
            else:
                engine_score = 0.0
            
            # Weighted combination
            target_score = (self.player_weight * player_score + 
                           self.engine_weight * engine_score)
            
            state["target_score"] = target_score
    
    def __len__(self) -> int:
        """Return number of examples in dataset"""
        return len(self.states)
    
    def __getitem__(self, idx: int) -> tuple:
        """
        Get a single training example
        
        Args:
            idx: Index of the example
            
        Returns:
            (board_tensor, target_score) tuple
            - board_tensor: (14, 8, 8) float tensor
            - target_score: scalar float tensor
        """
        state = self.states[idx]
        
        # Encode board state
        board_tensor = self.encoder.encode_board(state['fen'])
        
        # Get target score
        target_score = torch.tensor(state['target_score'], dtype=torch.float32)
        
        return board_tensor, target_score
    
    def __del__(self):
        """Clean up Stockfish engine on deletion"""
        if hasattr(self, 'engine') and self.engine is not None:
            try:
                self.engine.quit()
            except:
                pass
