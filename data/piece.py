"""Class and Enums to represent a single piece on a Chess Board"""

from enum import Enum


class PieceColor(Enum):
    """The color of a Piece."""

    WHITE = "White"
    BLACK = "Black"
    EMPTY = "Empty"


class PieceType(Enum):
    """The type of a Piece."""

    PAWN = "Pawn"
    KNIGHT = "Knight"
    BISHOP = "Bishop"
    ROOK = "Rook"
    QUEEN = "Queen"
    KING = "King"
    EMPTY = "Empty"


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

    def __str__(self):
        if (
            self.piece_color == PieceColor.EMPTY
            or self.piece_type == PieceType.EMPTY
        ):
            return str(PieceColor.EMPTY.value)
        else:
            return f"{self.piece_color.value} {self.piece_type.value}"
