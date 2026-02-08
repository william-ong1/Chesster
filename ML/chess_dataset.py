# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Chess dataset class for PyTorch DataLoader
# Loads board states and moves from MongoDB for training

import torch
from torch.utils.data import Dataset
from typing import List, Dict
import chess

class ChessDataset(Dataset):
    """
    PyTorch Dataset for chess training data
    """
    
    def __init__(self, states: List[Dict], encoder):
        """
        Initialize dataset
        
        Args:
            states: List of {fen, move_made, move_number} dictionaries
            encoder: StateEncoder instance for converting FEN to tensors
        """
        self.states = states
        self.encoder = encoder
        
        # Build move vocabulary
        self.move_to_idx = {}
        self.idx_to_move = {}
        self._build_move_vocabulary()
    
    def _build_move_vocabulary(self):
        """Build vocabulary of all possible moves"""
        # TODO: Either enumerate all possible chess moves (~4000)
        # or build vocabulary from training data
        pass
    
    def __len__(self) -> int:
        return len(self.states)
    
    def __getitem__(self, idx: int) -> tuple:
        """
        Get a single training example
        
        Args:
            idx: Index of the example
            
        Returns:
            (board_tensor, move_label) tuple
        """
        state = self.states[idx]
        
        # Encode board state
        board_tensor = self.encoder.encode_board(state['fen'])
        
        # Encode move as label
        move_san = state['move_made']
        move_label = self.move_to_idx.get(move_san, 0)  # 0 as unknown move
        
        return board_tensor, torch.tensor(move_label, dtype=torch.long)
