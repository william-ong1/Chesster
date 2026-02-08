# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Converts FEN board states to tensor representation for neural network
# Creates 12×8×8 tensors (12 piece-type channels) plus metadata channels

import chess
import torch
import numpy as np
from typing import List, Optional

class StateEncoder:
    """
    Converts chess board states (FEN) to neural network input tensors
    
    Encoding scheme:
    - 14 channels × 8 ranks × 8 files
    - Channels 0-5: White pieces (pawn, knight, bishop, rook, queen, king)
    - Channels 6-11: Black pieces (pawn, knight, bishop, rook, queen, king)
    - Channel 12: Castling rights encoded at specific positions
    - Channel 13: Turn and en passant square
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
    
    # Reverse mapping for decoding
    CHANNEL_TO_PIECE = {v: k for k, v in PIECE_TO_CHANNEL.items()}
    
    def __init__(self):
        """Initialize state encoder"""
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
            
        Raises:
            ValueError: If FEN string is invalid
        """
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {fen}") from e
        
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
        # Use specific board positions to encode castling availability
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
    
    def encode_batch(self, fens: List[str]) -> torch.Tensor:
        """
        Encode multiple FEN strings to batch tensor
        
        Args:
            fens: List of FEN strings
            
        Returns:
            Tensor of shape (batch_size, 14, 8, 8)
            
        Raises:
            ValueError: If any FEN string is invalid
        """
        if not fens:
            raise ValueError("Empty FEN list provided")
        
        return torch.stack([self.encode_board(fen) for fen in fens])
    
    def decode_board(self, tensor: torch.Tensor) -> str:
        """
        Decode tensor representation back to FEN string
        
        This is primarily useful for debugging and validation.
        
        Args:
            tensor: Board state tensor of shape (14, 8, 8)
            
        Returns:
            FEN string representation of the board
            
        Raises:
            ValueError: If tensor has invalid shape
        """
        if tensor.shape != (14, 8, 8):
            raise ValueError(f"Expected tensor shape (14, 8, 8), got {tensor.shape}")
        
        # Convert to numpy for easier indexing
        if isinstance(tensor, torch.Tensor):
            tensor = tensor.cpu().numpy()
        
        # Initialize empty board
        board = chess.Board(fen=None)
        board.clear()
        
        # Decode pieces from channels 0-11
        for square in chess.SQUARES:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            
            # Check white pieces (channels 0-5)
            for channel in range(6):
                if tensor[channel, rank, file] > 0.5:
                    piece_type = self.CHANNEL_TO_PIECE[channel]
                    board.set_piece_at(square, chess.Piece(piece_type, chess.WHITE))
                    break
            
            # Check black pieces (channels 6-11)
            for channel in range(6, 12):
                if tensor[channel, rank, file] > 0.5:
                    piece_type = self.CHANNEL_TO_PIECE[channel - 6]
                    board.set_piece_at(square, chess.Piece(piece_type, chess.BLACK))
                    break
        
        # Decode castling rights from channel 12
        castling_rights = chess.BB_EMPTY
        if tensor[12, 0, 0] > 0.5:  # White kingside
            castling_rights |= chess.BB_H1
        if tensor[12, 0, 1] > 0.5:  # White queenside
            castling_rights |= chess.BB_A1
        if tensor[12, 7, 0] > 0.5:  # Black kingside
            castling_rights |= chess.BB_H8
        if tensor[12, 7, 1] > 0.5:  # Black queenside
            castling_rights |= chess.BB_A8
        board.castling_rights = castling_rights
        
        # Decode turn from channel 13
        board.turn = chess.WHITE if tensor[13, 0, 0] > 0.5 else chess.BLACK
        
        # Decode en passant from channel 13
        for square in chess.SQUARES:
            if square == chess.A1:  # Skip turn indicator position
                continue
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            if tensor[13, rank, file] > 0.5:
                board.ep_square = square
                break
        
        return board.fen()
    
    def get_input_shape(self) -> tuple:
        """
        Get the expected input shape for neural networks
        
        Returns:
            Tuple (channels, height, width) = (14, 8, 8)
        """
        return (14, 8, 8)
