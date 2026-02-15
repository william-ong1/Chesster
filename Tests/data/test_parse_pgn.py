"""Tests the PGN cleaner class."""

from data.parse_pgn import ParsePGN
from data.board_state import BoardState
from typing import List


class TestPGNCleaner:
    """Tests the PGN cleaner class"""

    pgn_dir = "tests/data/pgn_test_files/"
    debug = False

    def test_parse_pgn_file(self):
        """Tests PGN files with data for a single game."""
        parser = ParsePGN()

        pgn2_fens = [
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "e4"),
            ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR", "e5"),
            ("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR", "Nf3"),
            ("rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R", "Nc6"),
            ("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R", "Bb5"),
            ("r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R", "1/2-1/2"),
        ]

        # non-existant PGN file
        pgn1 = self.pgn_dir + "non_existent.pgn"
        assert not parser.parse_file(pgn1)
        assert not parser.parsed_games

        # simple PGN file with no text other than moves
        pgn2 = self.pgn_dir + "no_headers.pgn"
        assert parser.parse_file(pgn2)
        game: List[BoardState] = parser.parsed_games[0]

        if self.debug:
            debug = "DEBUG: ["
            for move in game:
                debug += f"({move.fen}, {move.move}), "
            debug += "]"
            print(debug)
        assert len(game) == len(pgn2_fens)

        for i in range(0, len(pgn2_fens)):
            curr_state: BoardState = game[i]
            assert curr_state.fen.split(" ")[0] == pgn2_fens[i][0]
            assert parser.parsed_games[0][i].move == pgn2_fens[i][1]

    def test_parse_multiple_games(self):
        """Tests PGN files with data for multiple games."""
        parser = ParsePGN()
        multi_pgn = self.pgn_dir + "multiple_games.pgn"
        assert parser.parse_file(multi_pgn)

        game1 = parser.parsed_games[0]
        game1_final_fen = (
            "r1bq1rk1/ppp2ppp/8/4N3/3R4/4Q3/PPP2PPP/2K2B1R b - - 0 13"
        )
        game1_moves = 25
        game1_result = "1-0"
        assert len(game1) == game1_moves + 1
        assert game1[game1_moves].fen == game1_final_fen
        assert game1[game1_moves].move == game1_result

        game2 = parser.parsed_games[1]
        game2_final_fen = "8/6R1/3k3P/6K1/8/8/6r1/8 w - - 17 66"
        game2_moves = 130
        game2_result = "1/2-1/2"
        assert len(game2) == game2_moves + 1
        assert game2[game2_moves].fen == game2_final_fen
        assert game2[game2_moves].move == game2_result

        game3 = parser.parsed_games[2]
        game3_final_fen = "4r1k1/ppp2ppp/8/3P2r1/1PP1n3/P6Q/6PP/5q1K w - - 0 28"
        game3_moves = 54
        game3_result = "0-1"
        assert len(parser.parsed_games[2]) == game3_moves + 1
        assert game3[game3_moves].fen == game3_final_fen
        assert game3[game3_moves].move == game3_result
