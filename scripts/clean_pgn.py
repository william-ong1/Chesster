#!/usr/bin/env python3
"""
Preprocesses a PGN file for maia-individual compatibility.
- Joins multi-line move text into single lines
- Collapses multiple blank lines into one
Usage: python clean_pgn.py input.pgn output.pgn
"""
import re
import sys

def clean_pgn(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return
    except PermissionError:
        print(
            "Error: Permission denied. "
            f"Unable to access the file {input_path}."
        )
        return
    except OSError as e:
        print(f"An unexpected error occurred: {e}")
        return

    # Normalize line endings so \r\n and \r don't break game splitting
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = content.strip()
    if not content:
        print(f"Cleaned 0 games (file is empty) -> {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")
        return

    # Split into games: by double newline, or by line starting with [Event (new game)
    raw_chunks = re.split(r"\n{2,}", content)
    games = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        headers = [l.strip() for l in lines if l.strip().startswith("[")]
        moves = " ".join(l.strip() for l in lines if l.strip() and not l.strip().startswith("["))
        if headers and moves:
            games.append("\n".join(headers) + "\n\n" + moves + "\n")

    # If we still got 0 games, try splitting by [Event as start of each game (single-newline PGNs)
    if not games and "[Event " in content:
        game_blocks = re.split(r"\n(?=\[Event )", content)
        for chunk in game_blocks:
            chunk = chunk.strip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            headers = [l.strip() for l in lines if l.strip().startswith("[")]
            moves = " ".join(l.strip() for l in lines if l.strip() and not l.strip().startswith("["))
            if headers and moves:
                games.append("\n".join(headers) + "\n\n" + moves + "\n")

    fixed = games

    result = "\n".join(fixed)
    result = re.sub(r"\n{2,}", "\n\n", result)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
    except FileNotFoundError:
        print(f"Error: The file {output_path} was not found.")
        return
    except PermissionError:
        print(
            "Error: Permission denied. "
            f"Unable to access the file {output_path}."
        )
        return
    except OSError as e:
        print(f"An unexpected error occurred: {e}")
        return

    print(f"Cleaned {len(fixed)} games -> {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_pgn.py input.pgn output.pgn")
        sys.exit(1)
    clean_pgn(sys.argv[1], sys.argv[2])