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
    except PermissionError:
        print(
            "Error: Permission denied. \
            Unable to access the file {input_path}."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    games = content.strip().split("\n\n")
    fixed = []
    for chunk in games:
        lines = chunk.strip().split("\n")
        #Get all lines that start with brackets
        #these lines are not moves but contain annotations about the game.
        headers = [l for l in lines if l.startswith("[")]
        #Merge all lines containing moves into a single line
        moves = " ".join(l for l in lines \ 
                         if not l.startswith("[") and l.strip())
        if headers and moves:
            fixed.append('\n'.join(headers) + '\n\n' + moves + '\n')

    result = '\n'.join(fixed)
    result = re.sub(r'\n{2,}', '\n\n', result)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
    except FileNotFoundError:
        print(f"Error: The file {output_path} was not found.")
    except PermissionError:
        print(
            "Error: Permission denied. \
            Unable to access the file {output_path}."
        )
    except OSErrror as e:
        print(f"An unexpected error occurred: {e}")

    print(f"Cleaned {len(fixed)} games -> {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python clean_pgn.py input.pgn output.pgn")
        sys.exit(1)
    clean_pgn(sys.argv[1], sys.argv[2])
