# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Chess agent that uses trained evaluation networks with alpha-beta search
# Wraps model and provides move selection using minimax algorithm

import torch
import chess
from typing import Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(__file__))
from state_encoder import StateEncoder
from model_cache import ModelCache

class Agent:
    """
    Chess agent that uses trained neural network for position evaluation
    
    The agent:
    1. Loads a trained model from MongoDB (via ModelCache)
    2. Evaluates positions using the neural network
    3. Selects moves using alpha-beta pruning search
    """
    
    def __init__(
        self,
        model_id: str,
        search_depth: int = 3,
        model_cache: Optional[ModelCache] = None
    ):
        """
        Initialize agent with trained model
        
        Args:
            model_id: MongoDB model identifier
            search_depth: Depth of alpha-beta search (default 3 ply)
            model_cache: Optional ModelCache instance (creates new if None)
        """
        self.model_id = model_id
        self.search_depth = search_depth
        self.encoder = StateEncoder()
        
        # Load model from cache or database
        self.model_cache = model_cache or ModelCache()
        self._own_cache = model_cache is None
        
        self.model = self.model_cache.get(model_id)
        
        if self.model is None:
            raise ValueError(f"Model {model_id} not found")
        
        self.model.eval()  # Set to evaluation mode
        self.nodes_searched = 0
        
        print(f"✅ Agent initialized with model {model_id}, search depth {search_depth}")

    def get_move(self, board: chess.Board, depth: Optional[int] = None) -> chess.Move:
        """
        Get best move for current position using alpha-beta search
        
        Args:
            board: Current board state
            depth: Search depth (uses self.search_depth if None)
            
        Returns:
            Best move found
            
        Raises:
            ValueError: If no legal moves available
        """
        if board.is_game_over():
            raise ValueError("Game is over, no moves available")
        
        depth = depth or self.search_depth
        self.nodes_searched = 0
        
        # Get legal moves
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        # If only one move, return it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Order moves for better pruning (captures first, checks, etc.)
        ordered_moves = self._order_moves(board, legal_moves)
        
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Evaluate each move
        for move in ordered_moves:
            board.push(move)
            
            # Run alpha-beta search
            value = self._alpha_beta(
                board,
                depth - 1,
                alpha,
                beta,
                not board.turn  # Opposite color
            )
            
            board.pop()
            
            # Update best move
            if board.turn == chess.WHITE:
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
        
        print(f"🎯 Selected move: {best_move} (eval: {best_value:.3f}, nodes: {self.nodes_searched})")
        return best_move

    def _alpha_beta(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool
    ) -> float:
        """
        Alpha-beta pruning search
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player (White)
            
        Returns:
            Position evaluation score
        """
        self.nodes_searched += 1
        
        # Base case: reached depth limit or game over
        if depth == 0 or board.is_game_over():
            return self._evaluate_position(board)
        
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            # Checkmate or stalemate
            if board.is_checkmate():
                return float('-inf') if maximizing else float('inf')
            else:
                return 0.0  # Stalemate
        
        # Order moves for better pruning
        ordered_moves = self._order_moves(board, legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in ordered_moves:
                board.push(move)
                eval_score = self._alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                board.push(move)
                eval_score = self._alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval

    def _evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate position using neural network
        
        Args:
            board: Board state to evaluate
            
        Returns:
            Evaluation score (positive = White advantage, negative = Black advantage)
        """
        # Handle terminal positions
        if board.is_checkmate():
            return float('-inf') if board.turn == chess.WHITE else float('inf')
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        
        # Encode board state
        fen = board.fen()
        board_tensor = self.encoder.encode_board(fen).unsqueeze(0)  # Add batch dimension
        
        # Get neural network evaluation
        with torch.no_grad():
            evaluation = self.model(board_tensor).item()
        
        return evaluation

    def _order_moves(self, board: chess.Board, moves: list) -> list:
        """
        Order moves for better alpha-beta pruning efficiency
        
        Move ordering heuristics:
        1. Captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        2. Checks
        3. Other moves
        
        Args:
            board: Current board state
            moves: List of legal moves
            
        Returns:
            Ordered list of moves
        """
        def move_priority(move):
            score = 0
            
            # Captures (prioritize capturing valuable pieces)
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    # Piece values: P=1, N=3, B=3, R=5, Q=9
                    piece_values = {
                        chess.PAWN: 1,
                        chess.KNIGHT: 3,
                        chess.BISHOP: 3,
                        chess.ROOK: 5,
                        chess.QUEEN: 9,
                        chess.KING: 0
                    }
                    score += piece_values.get(captured_piece.piece_type, 0) * 10
            
            # Checks
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()
            
            # Promotions
            if move.promotion:
                score += 100
            
            return -score  # Negative because we want higher scores first
        
        return sorted(moves, key=move_priority)

    def evaluate_board(self, board: chess.Board) -> float:
        """
        Evaluate a board position without search (direct neural network evaluation)
        
        Args:
            board: Board state to evaluate
            
        Returns:
            Evaluation score
        """
        return self._evaluate_position(board)

    def get_nodes_searched(self) -> int:
        """
        Get number of nodes searched in last move
        
        Returns:
            Node count
        """
        return self.nodes_searched

    def set_search_depth(self, depth: int):
        """
        Update search depth
        
        Args:
            depth: New search depth (ply)
        """
        self.search_depth = depth
        print(f"🔧 Search depth updated to {depth}")

    def close(self):
        """Close resources"""
        if self._own_cache and self.model_cache:
            self.model_cache.close()

    def __del__(self):
        """Cleanup on deletion"""
        self.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
