"""Class and Enums to represent a single piece on a Chess Board"""

from enum import Enum


class PieceColor(Enum):
    """The color of a Piece."""

    WHITE = "white"
    BLACK = "black"
    EMPTY = "empty"


class PieceType(Enum):
    """The type of a Piece."""

    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"
    EMPTY = "empty"


class Piece:
    """
    Represents a single board piece.

    Fields:
        piece_color: the color of the piece.
        piece_type: the piece's type.
    """

    def __init__(self, color: PieceColor, piece_type: PieceType):
        """
        Initializes a Piece.

        Args:
            color: the color of the piece
            piece_type: the piece's type
        """
        self.piece_color = color
        self.piece_type = piece_type
