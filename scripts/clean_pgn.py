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
    with open(input_path, 'r') as f:
        content = f.read()

    games = content.strip().split('\n\n')
    fixed = []
    for chunk in games:
        lines = chunk.strip().split('\n')
        headers = [l for l in lines if l.startswith('[')]
        moves = ' '.join(l for l in lines if not l.startswith('[') and l.strip())
        if headers and moves:
            fixed.append('\n'.join(headers) + '\n\n' + moves + '\n')

    result = '\n'.join(fixed)
    result = re.sub(r'\n{2,}', '\n\n', result)

    with open(output_path, 'w') as f:
        f.write(result)

    print(f"Cleaned {len(fixed)} games -> {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python clean_pgn.py input.pgn output.pgn")
        sys.exit(1)
    clean_pgn(sys.argv[1], sys.argv[2])