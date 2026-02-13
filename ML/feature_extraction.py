 # given a board object, extract the features of the board state and return them as a tensor
 # the features right now are the 
 # white king in check, black king in check, 
 # white queen is threatened, black queen is threatened, 
 # white rook is threatened, black rook is threatened, 
 # white bishop is threatened, black bishop is threatened, 
 # white knight is threatened, black knight is threatened, 
 # white pawn is threatened, black pawn is threatened
 # the pawn boards for white and black
 # the number of squares controlled by white and black
 # the material count for white and black

from tabnanny import check
import torch
import chess

class FeatureExtraction:
    def __init__(self, board: chess.Board):
        self.board = board

    def extract_features(self) -> torch.Tensor:
        # White/black king in check: king square attacked by the opposite color
        check_white = self.is_checked(chess.WHITE)
        check_black = self.is_checked(chess.BLACK)
        queen_threatened_white = self.is_threatened(chess.PieceType.QUEEN, chess.WHITE)
        queen_threatened_black = self.is_threatened(chess.PieceType.QUEEN, chess.BLACK)
        rook_threatened_white = self.is_threatened(chess.PieceType.ROOK, chess.WHITE)
        rook_threatened_black = self.is_threatened(chess.PieceType.ROOK, chess.BLACK)
        bishop_threatened_white = self.is_threatened(chess.PieceType.BISHOP, chess.WHITE)
        bishop_threatened_black = self.is_threatened(chess.PieceType.BISHOP, chess.BLACK)
        knight_threatened_white = self.is_threatened(chess.PieceType.KNIGHT, chess.WHITE)
        knight_threatened_black = self.is_threatened(chess.PieceType.KNIGHT, chess.BLACK)
        pawn_threatened_white = self.is_threatened(chess.PieceType.PAWN, chess.WHITE)
        pawn_threatened_black = self.is_threatened(chess.PieceType.PAWN, chess.BLACK)
        pawn_board_white = self.pawn_board(chess.WHITE)
        pawn_board_black = self.pawn_board(chess.BLACK)
        squares_controlled_white = self._squares_controlled_count(chess.WHITE)
        squares_controlled_black = self._squares_controlled_count(chess.BLACK)
        material_count_white = self.material_count(chess.WHITE)
        material_count_black = self.material_count(chess.BLACK)
        features = torch.tensor([check_white, check_black, queen_threatened_white, queen_threatened_black, rook_threatened_white, rook_threatened_black, bishop_threatened_white, bishop_threatened_black, knight_threatened_white, knight_threatened_black, pawn_threatened_white, pawn_threatened_black, pawn_board_white, pawn_board_black, squares_controlled_white, squares_controlled_black, material_count_white, material_count_black])
        return features
    
    def _squares_controlled_count(self, color: chess.Color) -> int:
        """Return the number of squares attacked by pieces of the given color."""
        return sum(1 for sq in chess.SQUARES if self.board.is_attacked_by(color, sq))

    def is_checked(self, color: chess.Color) -> bool:
        """Return True if the given side's king is in check."""
        king_square = self.board.king(color)
        if king_square is None:
            return False
        opponent = chess.BLACK if color == chess.WHITE else chess.WHITE
        return self.board.is_attacked_by(opponent, king_square)
        
    def is_threatened(self, piece: chess.PieceType, color: chess.Color ) -> bool:
        
        for square in chess.SQUARES:
            if self.board.piece_at(square) is not None and self.board.piece_at(square).color == color and self.board.piece_at(square).piece_type == piece:
                if self.board.is_attacked_by(not color, square):
                    return True
        return False

    def material_count(self, color: chess.Color) -> int:
        """Return the material count for the given color."""
        return self.board.material_count(color)

    def pawn_board(self, color: chess.Color) -> torch.Tensor:
        """Return the pawn board for the given color."""
        return torch.tensor([1 if self.board.piece_at(square) is not None and self.board.piece_at(square).color == color and self.board.piece_at(square).piece_type == chess.PieceType.PAWN else 0 for square in chess.SQUARES])