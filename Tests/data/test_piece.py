"""Tests the piece module."""

from data.piece import Piece, PieceColor, PieceType


class TestPiece:
    """Tests the Piece class."""

    pieces = {
        "White Pawn": Piece(PieceColor.WHITE, PieceType.PAWN),
        "Black Pawn": Piece(PieceColor.BLACK, PieceType.PAWN),
        "White Knight": Piece(PieceColor.WHITE, PieceType.KNIGHT),
        "White Bishop": Piece(PieceColor.WHITE, PieceType.BISHOP),
        "White Rook": Piece(PieceColor.WHITE, PieceType.ROOK),
        "White Queen": Piece(PieceColor.WHITE, PieceType.QUEEN),
        "White King": Piece(PieceColor.WHITE, PieceType.KING),
        "Empty": Piece(PieceColor.EMPTY, PieceType.EMPTY),
    }

    def correct_piece(
        self, piece: Piece, piece_color: PieceColor, piece_type: PieceType
    ) -> bool:
        return (
            piece.piece_color == piece_color and piece.piece_type == piece_type
        )

    def test_piece_constructor(self):
        # pieces = {
        #     "White Pawn": Piece(PieceColor.WHITE, PieceType.PAWN),
        #     "Black Pawn": Piece(PieceColor.BLACK, PieceType.PAWN),
        #     "white knight": Piece(PieceColor.WHITE, PieceType.KNIGHT),
        #     "white bishop": Piece(PieceColor.WHITE, PieceType.BISHOP),
        #     "White Rook": Piece(PieceColor.WHITE, PieceType.ROOK),
        #     "White Queen": Piece(PieceColor.WHITE, PieceType.QUEEN),
        #     "White King": Piece(PieceColor.WHITE, PieceType.KING),
        #     "empty": Piece(PieceColor.EMPTY, PieceType.EMPTY),
        # }

        assert self.correct_piece(
            self.pieces.get("White Pawn"), PieceColor.WHITE, PieceType.PAWN
        )
        assert self.correct_piece(
            self.pieces.get("Black Pawn"), PieceColor.BLACK, PieceType.PAWN
        )
        assert self.correct_piece(
            self.pieces.get("White Knight"), PieceColor.WHITE, PieceType.KNIGHT
        )
        assert self.correct_piece(
            self.pieces.get("White Bishop"), PieceColor.WHITE, PieceType.BISHOP
        )
        assert self.correct_piece(
            self.pieces.get("White Rook"), PieceColor.WHITE, PieceType.ROOK
        )
        assert self.correct_piece(
            self.pieces.get("White Queen"), PieceColor.WHITE, PieceType.QUEEN
        )
        assert self.correct_piece(
            self.pieces.get("White King"), PieceColor.WHITE, PieceType.KING
        )
        assert self.correct_piece(
            self.pieces.get("Empty"), PieceColor.EMPTY, PieceType.EMPTY
        )

    def test_to_str(self):
        assert str(self.pieces.get("White Pawn")) == "White Pawn"
        assert str(self.pieces.get("Black Pawn")) == "Black Pawn"
        assert str(self.pieces.get("White Bishop")) == "White Bishop"
        assert str(self.pieces.get("Empty")) == "Empty"
