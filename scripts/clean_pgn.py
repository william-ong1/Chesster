#!/usr/bin/env python3
"""
Preprocesses a PGN file for maia-individual compatibility.
- Joins multi-line move text into single lines
- Collapses multiple blank lines into one
Usage: python clean_pgn.py input.pgn output.pgn
"""
import re
import sys
import argparse

def clean_pgn(input_path, output_path, min_games=0):
    """
    Cleans a PGN file and writes the cleaned output.

    If min_games > 0, raises ValueError when fewer than min_games games
    are found.
    Returns the number of cleaned games written.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as in_file:
            content = in_file.read()
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return 0
    except PermissionError:
        print(
            "Error: Permission denied. "
            f"Unable to access the file {input_path}."
        )
        return 0
    except OSError as err:
        print(f"An unexpected error occurred: {err}")
        return 0

    # Normalize line endings so \r\n and \r don't break game splitting
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = content.strip()
    if not content:
        if min_games and min_games > 0:
            raise ValueError(
                f"At least {min_games} games are required. "
                "Your PGN has 0 games (file is empty)."
            )
        try:
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write("")
        except FileNotFoundError:
            print(f"Error: The file {output_path} was not found.")
            return 0
        except PermissionError:
            print(
                "Error: Permission denied. "
                f"Unable to access the file {output_path}."
            )
            return 0
        except OSError as err:
            print(f"An unexpected error occurred: {err}")
            return 0
        print(f"Cleaned 0 games (file is empty) -> {output_path}")
        return 0

    # Split games by double newline or [Event header
    raw_chunks = re.split(r"\n{2,}", content)
    games = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        headers = [
            ln.strip() for ln in lines if ln.strip().startswith("[")
        ]
        moves = " ".join(
            ln.strip() for ln in lines
            if ln.strip() and not ln.strip().startswith("[")
        )
        if headers and moves:
            games.append("\n".join(headers) + "\n\n" + moves + "\n")

    # Fallback: split by [Event for single-newline PGNs
    if not games and "[Event " in content:
        game_blocks = re.split(r"\n(?=\[Event )", content)
        for chunk in game_blocks:
            chunk = chunk.strip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            headers = [
                ln.strip() for ln in lines
                if ln.strip().startswith("[")
            ]
            moves = " ".join(
                ln.strip() for ln in lines
                if ln.strip()
                and not ln.strip().startswith("[")
            )
            if headers and moves:
                games.append("\n".join(headers) + "\n\n" + moves + "\n")

    if min_games and min_games > 0 and len(games) < min_games:
        raise ValueError(
            f"At least {min_games} games are required. "
            f"Your PGN has {len(games)} game(s)."
        )

    result = "\n".join(games)
    result = re.sub(r"\n{2,}", "\n\n", result)

    try:
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(result)
    except FileNotFoundError:
        print(f"Error: The file {output_path} was not found.")
        return 0
    except PermissionError:
        print(
            "Error: Permission denied. "
            f"Unable to access the file {output_path}."
        )
        return 0
    except OSError as err:
        print(f"An unexpected error occurred: {err}")
        return 0

    print(f"Cleaned {len(games)} games -> {output_path}")
    return len(games)

if __name__ == "__main__":
    class _ExitCodeOneArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            print("Usage:", file=sys.stdout)
            self.print_usage(sys.stdout)
            print(f"{self.prog}: error: {message}", file=sys.stderr)
            raise SystemExit(1)

    parser = _ExitCodeOneArgumentParser(
        description="Preprocess a PGN for maia-individual compatibility."
    )
    parser.add_argument("input_path", help="input PGN path")
    parser.add_argument("output_path", help="output PGN path")
    parser.add_argument(
        "--min-games",
        type=int,
        default=0,
        help="minimum required games; 0 disables the check",
    )
    args = parser.parse_args()

    try:
        clean_pgn(args.input_path, args.output_path, min_games=args.min_games)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
