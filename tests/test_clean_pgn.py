"""Tests for scripts/clean_pgn.py"""
# pylint: disable=redefined-outer-name
# 65 statements, 6 missed, 91% coverage

import subprocess
import sys
from unittest import mock
import pytest
from scripts.clean_pgn import clean_pgn


@pytest.fixture
def tmp_paths(tmp_path):
    """Provide temporary input/output file paths."""
    input_file = tmp_path / "input.pgn"
    output_file = tmp_path / "output.pgn"
    return input_file, output_file


SINGLE_GAME = (
    '[Event "Rated Blitz game"]\n'
    '[White "Alice"]\n'
    '[Black "Bob"]\n'
    '[Result "1-0"]\n'
    "\n"
    "1. e4 e5 2. Nf3 Nc6 1-0\n"
)

TWO_GAMES = (
    '[Event "Game 1"]\n'
    '[White "Alice"]\n'
    '[Black "Bob"]\n'
    '[Result "1-0"]\n'
    "\n"
    "1. e4 e5 1-0\n"
    "\n"
    '[Event "Game 2"]\n'
    '[White "Carol"]\n'
    '[Black "Dave"]\n'
    '[Result "0-1"]\n'
    "\n"
    "1. d4 d5 0-1\n"
)


class TestCleanPgnBasic:
    """Core formatting behaviour."""

    def test_single_game_preserves_headers_and_moves(self, tmp_paths):
        """A well-formed single game should come through intact."""
        inp, out = tmp_paths
        inp.write_text(SINGLE_GAME)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert '[Event "Rated Blitz game"]' in result
        assert '[White "Alice"]' in result
        assert "1. e4 e5 2. Nf3 Nc6 1-0" in result

    def test_two_games_both_present(self, tmp_paths):
        """Multiple games separated by blank lines should all be kept."""
        inp, out = tmp_paths
        inp.write_text(TWO_GAMES)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert '[Event "Game 1"]' in result
        assert '[Event "Game 2"]' in result
        assert "1. e4 e5 1-0" in result
        assert "1. d4 d5 0-1" in result

    def test_multiline_moves_joined(self, tmp_paths):
        """Move text split across lines should be joined into one line."""
        inp, out = tmp_paths
        pgn = (
            '[Event "Test"]\n'
            '[Result "1-0"]\n'
            "\n"
            "1. e4 e5\n"
            "2. Nf3 Nc6\n"
            "3. Bb5 1-0\n"
        )
        inp.write_text(pgn)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0" in result

    def test_extra_blank_lines_collapsed(self, tmp_paths):
        """Runs of 3+ blank lines between games should collapse to one."""
        inp, out = tmp_paths
        pgn = (
            '[Event "G1"]\n[Result "1-0"]\n\n1. e4 1-0\n'
            "\n\n\n\n"
            '[Event "G2"]\n[Result "0-1"]\n\n1. d4 0-1\n'
        )
        inp.write_text(pgn)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert "\n\n\n" not in result


class TestCleanPgnEdgeCases:
    """Boundary and error conditions."""

    def test_empty_file_produces_empty_output(self, tmp_paths):
        """An empty input should produce an empty output file."""
        inp, out = tmp_paths
        inp.write_text("")
        clean_pgn(str(inp), str(out))

        assert out.read_text() == ""

    def test_whitespace_only_file(self, tmp_paths):
        """A file with only whitespace should be treated as empty."""
        inp, out = tmp_paths
        inp.write_text("   \n\n  \n  ")
        clean_pgn(str(inp), str(out))

        assert out.read_text() == ""

    def test_headers_only_no_moves_skipped(self, tmp_paths):
        """A game block with headers but no moves should be omitted."""
        inp, out = tmp_paths
        pgn = '[Event "No moves"]\n[White "Alice"]\n[Black "Bob"]\n'
        inp.write_text(pgn)
        clean_pgn(str(inp), str(out))

        assert out.read_text().strip() == ""

    def test_windows_line_endings_normalized(self, tmp_paths):
        r"""\\r\\n line endings should be handled without breaking parsing."""
        inp, out = tmp_paths
        pgn = (
            '[Event "Test"]\r\n'
            '[Result "1-0"]\r\n'
            "\r\n"
            "1. e4 e5 1-0\r\n"
        )
        inp.write_bytes(pgn.encode("utf-8"))
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert '[Event "Test"]' in result
        assert "1. e4 e5 1-0" in result

    def test_missing_input_file_does_not_crash(self, tmp_paths, capsys):
        """A nonexistent input path should print an error, not raise."""
        _, out = tmp_paths
        clean_pgn("/no/such/file.pgn", str(out))

        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_permission_error_on_input(self, tmp_paths, capsys):
        """PermissionError reading input prints an error."""
        inp, out = tmp_paths
        inp.write_text("data")
        with mock.patch(
            "builtins.open", side_effect=PermissionError
        ):
            clean_pgn(str(inp), str(out))
        captured = capsys.readouterr()
        assert "Permission denied" in captured.out

    def test_os_error_on_input(self, tmp_paths, capsys):
        """Generic OSError reading input prints an error."""
        inp, out = tmp_paths
        inp.write_text("data")
        with mock.patch(
            "builtins.open", side_effect=OSError("disk failure")
        ):
            clean_pgn(str(inp), str(out))
        captured = capsys.readouterr()
        assert "disk failure" in captured.out

    def test_output_to_invalid_directory(self, tmp_paths, capsys):
        """Writing to a nonexistent directory prints an error."""
        inp, _ = tmp_paths
        inp.write_text(SINGLE_GAME)
        bad_out = "/no/such/dir/output.pgn"
        clean_pgn(str(inp), bad_out)
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_permission_error_on_output(self, tmp_paths, capsys):
        """PermissionError writing output prints an error."""
        inp, out = tmp_paths
        inp.write_text(SINGLE_GAME)
        real_open = open

        def selective_open(*args, **kwargs):
            if args[0] == str(out) and args[1] == "w":
                raise PermissionError
            return real_open(*args, **kwargs)

        with mock.patch("builtins.open", side_effect=selective_open):
            clean_pgn(str(inp), str(out))
        captured = capsys.readouterr()
        assert "Permission denied" in captured.out

    def test_os_error_on_output(self, tmp_paths, capsys):
        """Generic OSError writing output prints an error."""
        inp, out = tmp_paths
        inp.write_text(SINGLE_GAME)
        real_open = open

        def selective_open(*args, **kwargs):
            if args[0] == str(out) and args[1] == "w":
                raise OSError("no space left")
            return real_open(*args, **kwargs)

        with mock.patch("builtins.open", side_effect=selective_open):
            clean_pgn(str(inp), str(out))
        captured = capsys.readouterr()
        assert "no space left" in captured.out


class TestCleanPgnSingleNewlineSplit:
    """Games separated by single newlines (fallback [Event split)."""

    def test_single_newline_separated_games(self, tmp_paths):
        """Games with only one newline between them should still be split."""
        inp, out = tmp_paths
        pgn = (
            '[Event "G1"]\n[Result "1-0"]\n1. e4 1-0\n'
            '[Event "G2"]\n[Result "0-1"]\n1. d4 0-1\n'
        )
        inp.write_text(pgn)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert '[Event "G1"]' in result
        assert '[Event "G2"]' in result

    def test_single_newline_with_empty_chunks(self, tmp_paths):
        """Blank lines mixed into single-newline games are skipped."""
        inp, out = tmp_paths
        pgn = (
            "\n\n"
            '[Event "G1"]\n[Result "1-0"]\n1. e4 1-0\n'
        )
        inp.write_text(pgn)
        clean_pgn(str(inp), str(out))

        result = out.read_text()
        assert "1. e4 1-0" in result


class TestCleanPgnMainBlock:
    """The __main__ CLI entrypoint."""

    def test_main_with_valid_args(self, tmp_paths):
        """Running as a script with two args should succeed."""
        inp, out = tmp_paths
        inp.write_text(SINGLE_GAME)
        result = subprocess.run(
            [sys.executable, "scripts/clean_pgn.py",
             str(inp), str(out)],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0
        assert "Cleaned 1 games" in result.stdout

    def test_main_with_wrong_arg_count(self):
        """Running with no args should exit with code 1."""
        result = subprocess.run(
            [sys.executable, "scripts/clean_pgn.py"],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 1
        assert "Usage" in result.stdout
