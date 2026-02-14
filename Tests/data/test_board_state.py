"""Tests the BoardState class."""

from data.board_state import BoardState

from data.piece import Piece, PieceType, PieceColor
import pytest


class TestBoardState:
    """Tests the BoardState class."""

    def correct_piece(self, actual: Piece, expected: Piece) -> bool:
        """
        Checks if two pieces are equal.

        Args:
            actual: the actual Piece.
            expected: the expected value of the Piece.

        Returns:
            True if the pieces have equal color and type. False otherwise.
        """
        return (
            actual.color == expected.color
            and actual.piece_type == expected.piece_type
        )

    def test_get_piece(self):
        """Test get_piece() functionality."""

        fen1 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        state = BoardState(fen1, "e4")

        # valid pieces
        assert self.correct_piece(
            state.get_piece("p"), Piece(PieceColor.BLACK, PieceType.PAWN)
        )
        assert self.correct_piece(
            state.get_piece("P"), Piece(PieceColor.WHITE, PieceType.PAWN)
        )
        assert self.correct_piece(
            state.get_piece("n"), Piece(PieceColor.BLACK, PieceType.KNIGHT)
        )
        assert self.correct_piece(
            state.get_piece("b"), Piece(PieceColor.BLACK, PieceType.BISHOP)
        )
        assert self.correct_piece(
            state.get_piece("r"), Piece(PieceColor.BLACK, PieceType.ROOK)
        )
        assert self.correct_piece(
            state.get_piece("q"), Piece(PieceColor.BLACK, PieceType.QUEEN)
        )
        assert self.correct_piece(
            state.get_piece("k"), Piece(PieceColor.BLACK, PieceType.KING)
        )

        # '/' character
        assert state.get_piece("/") is None

        # invalid piece: multiple characters
        with pytest.raises(ValueError):
            state.get_piece("kn")
        # invalid piece: number
        with pytest.raises(ValueError):
            state.get_piece("1")
        # invalid piece: bad character
        with pytest.raises(ValueError):
            state.get_piece("x")

    def test_fen_to_list(self):
        """Test fen_to_list() functionality."""

        # starting position
        fen1 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board_state1 = BoardState(fen1, "e4")
        assert len(board_state1.pieces) == 64
        # one of the black pieces
        assert self.correct_piece(
            board_state1.pieces[0],
            Piece(PieceColor.BLACK, PieceType.ROOK),
        )
        # one of the black pawns
        assert self.correct_piece(
            board_state1.pieces[8],
            Piece(PieceColor.BLACK, PieceType.PAWN),
        )
        # one of the empty squares
        assert self.correct_piece(
            board_state1.pieces[16],
            Piece(PieceColor.EMPTY, PieceType.EMPTY),
        )
        # one of the white pawns
        assert self.correct_piece(
            board_state1.pieces[50],
            Piece(PieceColor.WHITE, PieceType.PAWN),
        )
        # one of the white pieces
        assert self.correct_piece(
            board_state1.pieces[57],
            Piece(PieceColor.WHITE, PieceType.KNIGHT),
        )

        # empty position
        fen2 = "8/8/8/8/8/8/8/8 w - - 0 1"
        board_state2 = BoardState(fen2, "e4")
        assert len(board_state2.pieces) == 64
        for piece in board_state2.pieces:
            assert self.correct_piece(
                piece, Piece(PieceColor.EMPTY, PieceType.EMPTY)
            )
