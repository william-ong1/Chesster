# (C) Chesster. Written by Shreyan Mitra, William Ong,
# Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Parses PGN text to structured game data using python-chess
# Extracts metadata (ELO, time control, results)

import chess.pgn
import io
from typing import List
from .board_state import BoardState


class ParsePGN:
    """
    Converts PGN text to structured game data.
    The final move of a game is notated as 1-0 if White wins,
    0-1 if Black wins, and 1/2-1/2 for a draw or stalemate.

    Fields:
        parsed_games: A list of all games parsed by this Parser.
        Each game consists of a list of BoardStates.
    """

    def __init__(self):
        self.parsed_games: List[List[BoardState]] = []

    def parse_file(self, filename: str) -> bool:
        """
        Parses a PGN file, converting it into a list of games.
        Each game consists of a list of BoardStates. If the file is parsed
        successfullly, the results are stored in the parsed_games field.

        Args:
            filename: the name of the PGN file to parse.

        Returns:
            True if the file is successfully parsed.
            False if the passed file is invalid.
        """
        try:
            pgn_txt = open(filename, encoding="utf-8")
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return False
        except OSError as e:
            print(f"An OS error occurred: {e}")
            return False

        parsed = False
        with pgn_txt:
            parsed = self.parse_string(pgn_txt.read())
            pgn_txt.close()

        return parsed

    def parse_string(self, pgn_text: str) -> bool:
        """
        Parse PGN text into a list of BoardStates.
        Appends successfully parsed games to the parsed_games field.

        Args:
            pgn_text: Raw PGN string (can contain multiple games)

        Returns:
            True if at least one game was successfully parsed from the string.
            False otherwise.
        """
        pgn_io = io.StringIO(pgn_text)

        success = False
        while True:
            # Automatically skips tokens it can't parse
            game = chess.pgn.read_game(pgn_io)

            # End of file reached
            if game is None:
                break

            moves = self._extract_moves(game)

            # Only add game if all moves were valid
            if moves:
                success = True
                self.parsed_games.append(moves)

        return success

    def _extract_moves(self, game: chess.pgn.Game) -> List[BoardState]:
        """
        Extract the sequence of moves from a game.

        Args:
            game: python-chess Game object

        Returns:
            List of BoardStates
        """

        moves_to_board_state = []
        board = game.board()
        for move in game.mainline_moves():
            # validate moves
            if board.is_legal(move):
                move_txt = board.san(move)
                fen = board.fen()
                curr_state = BoardState(fen=fen, move=move_txt)
                board.push(move)

                moves_to_board_state.append(curr_state)
            else:
                print(f"Invalid move: {move}")
                return []

        win_move = game.headers["Result"]
        final_board_state = BoardState(board.fen(), win_move)
        moves_to_board_state.append(final_board_state)
        return moves_to_board_state
