# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Converts FEN board states to tensor representation for neural network
# Creates 12×8×8 tensors (12 piece-type channels) plus metadata channels

import chess
import torch
import numpy as np
from typing import Tuple

class StateEncoder:
    """
    Converts chess board states (FEN) to neural network input tensors
    """
    
    # Piece type to channel mapping
    PIECE_TO_CHANNEL = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5
    }
    
    def __init__(self):
        pass
    
    def encode_board(self, fen: str) -> torch.Tensor:
        """
        Encode FEN string to tensor representation
        
        Args:
            fen: Board state in FEN notation
            
        Returns:
            Tensor of shape (14, 8, 8) representing the board state
            - 12 channels for piece types (6 white, 6 black)
            - 1 channel for castling rights
            - 1 channel for en passant and turn
        """
        board = chess.Board(fen)
        
        # Initialize 14 channels (12 pieces + 2 metadata)
        tensor = np.zeros((14, 8, 8), dtype=np.float32)
        
        # Encode pieces (channels 0-11)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                # Get rank and file (row, col)
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                
                # Get channel index (0-5 for piece type, +6 if black)
                channel = self.PIECE_TO_CHANNEL[piece.piece_type]
                if piece.color == chess.BLACK:
                    channel += 6
                
                tensor[channel, rank, file] = 1.0
        
        # Encode castling rights (channel 12)
        tensor[12, 0, 0] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
        tensor[12, 0, 1] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
        tensor[12, 7, 0] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
        tensor[12, 7, 1] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0
        
        # Encode turn and en passant (channel 13)
        tensor[13, 0, 0] = 1.0 if board.turn == chess.WHITE else 0.0
        if board.ep_square is not None:
            ep_rank = chess.square_rank(board.ep_square)
            ep_file = chess.square_file(board.ep_square)
            tensor[13, ep_rank, ep_file] = 1.0
        
        return torch.from_numpy(tensor)
    
    def encode_batch(self, fens: list) -> torch.Tensor:
        """
        Encode multiple FEN strings to batch tensor
        
        Args:
            fens: List of FEN strings
            
        Returns:
            Tensor of shape (batch_size, 14, 8, 8)
        """
        return torch.stack([self.encode_board(fen) for fen in fens])
