from enum import Enum


class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"
    EMPTY = "empty"


class PieceType(Enum):
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"
    EMPTY = "empty"


class Piece:
    def __init__(self, color: PieceColor, piece_type: PieceType):
        self.color = color
        self.piece_type = piece_type
