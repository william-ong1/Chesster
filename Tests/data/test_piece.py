"""Tests the piece module."""

from data.piece import Piece, PieceColor, PieceType


class TestPiece:
    """Tests the Piece class."""

    def correct_piece(
        self, piece: Piece, piece_color: PieceColor, piece_type: PieceType
    ) -> bool:
        return (
            piece.piece_color == piece_color and piece.piece_type == piece_type
        )

    def test_piece_constructor(self):
        pieces = {
            "white pawn": Piece(PieceColor.WHITE, PieceType.PAWN),
            "black pawn": Piece(PieceColor.BLACK, PieceType.PAWN),
            "white knight": Piece(PieceColor.WHITE, PieceType.KNIGHT),
            "white bishop": Piece(PieceColor.WHITE, PieceType.BISHOP),
            "white rook": Piece(PieceColor.WHITE, PieceType.ROOK),
            "white queen": Piece(PieceColor.WHITE, PieceType.QUEEN),
            "white king": Piece(PieceColor.WHITE, PieceType.KING),
            "empty": Piece(PieceColor.EMPTY, PieceType.EMPTY),
        }

        assert self.correct_piece(
            pieces.get("white pawn"), PieceColor.WHITE, PieceType.PAWN
        )
        assert self.correct_piece(
            pieces.get("black pawn"), PieceColor.BLACK, PieceType.PAWN
        )
        assert self.correct_piece(
            pieces.get("white knight"), PieceColor.WHITE, PieceType.KNIGHT
        )
        assert self.correct_piece(
            pieces.get("white bishop"), PieceColor.WHITE, PieceType.BISHOP
        )
        assert self.correct_piece(
            pieces.get("white rook"), PieceColor.WHITE, PieceType.ROOK
        )
        assert self.correct_piece(
            pieces.get("white queen"), PieceColor.WHITE, PieceType.QUEEN
        )
        assert self.correct_piece(
            pieces.get("white king"), PieceColor.WHITE, PieceType.KING
        )
        assert self.correct_piece(
            pieces.get("empty"), PieceColor.EMPTY, PieceType.EMPTY
        )
