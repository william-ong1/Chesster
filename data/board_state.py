"""Used to represent a Board State"""

from data.piece import Piece, PieceColor, PieceType


class BoardState:
    """
    A representation of a board state after a given move.

    Fields:
        _valid_pieces: the list of valid pieces in FEN notation.
        fen: the FEN representation of the board state.
        move: the move that resulted in this board state.
        pieces: the board state represented as a length-64 array.
        features: the features of the board state.
    """

    def __init__(self, fen: str, move: str):
        """
        Docstring for __init__

        Args:
            fen: the FEN representation of the board state.
            move: the move that resulted in this board state.
        """
        self._valid_pieces = "rnbqkpRNBQKP/"
        self.move = move
        self.fen = fen
        self.pieces = self._fen_to_list()
        # TODO: update this based on Feature Extraction code
        self.features = {}

    def _fen_to_list(self) -> list[Piece]:
        """
        Converts FEN into a length-64 array of Pieces.
        The board position described by the FEN is assumed to be valid.

        Returns:
            A length-64 List of Pieces.

        Exceptions:
            ValueError if the FEN notation is invalid
        """
        piece_list = []
        # only use the FEN that represents the board state
        board = self.fen.split()[0]
        for char in board:
            if char.isdigit():
                for _ in range(0, int(char)):
                    piece_list.append(Piece(PieceColor.EMPTY, PieceType.EMPTY))
            else:
                piece = self.get_piece(char)
                if piece is not None:
                    piece_list.append(piece)

        if len(piece_list) != 64:
            raise ValueError(
                f"Invalid FEN: expected 64 pieces, got {len(piece_list)}"
            )

        return piece_list

    def get_piece(self, char: str):
        """
        Given a character, returns a Piece representation.
        The character must be a valid chess piece in FEN notation.

        Args:
            char: the character to be converted to a Piece.

        Returns:
            None if the given character is '/'.
            A Piece representation of a valid character.

        Exceptions:
            ValueError if the given string is a number, an invalid piece,
            or longer than a single character.
        """
        if len(char) != 1:
            raise ValueError("Input must be a single character.")
        if char.isdigit():
            raise ValueError("Input cannot be a number.")
        if char not in self._valid_pieces:
            raise ValueError(f"Invalid piece character: {char}")

        # The '/' denotes the end of a row
        if char == "/":
            return None

        if char.isupper():
            color = PieceColor.WHITE
        else:
            color = PieceColor.BLACK

        piece_type = {
            "p": PieceType.PAWN,
            "n": PieceType.KNIGHT,
            "b": PieceType.BISHOP,
            "r": PieceType.ROOK,
            "q": PieceType.QUEEN,
            "k": PieceType.KING,
        }.get(char.lower())

        return Piece(color, piece_type)

    def __str__(self):
        return f"({self.fen}, {self.move})"
