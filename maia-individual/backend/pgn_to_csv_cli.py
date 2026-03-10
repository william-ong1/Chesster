#!/usr/bin/env python3
"""Convert PGN file to CSV for prediction_generator evaluation."""

import argparse
import bz2
import os
import sys

# Ensure backend is importable when run from 1-data_generation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend
from backend.pgn_to_csv import gameToCSVlines, full_csv_header


def main():
    parser = argparse.ArgumentParser(description='Convert PGN to CSV for evaluation')
    parser.add_argument('input', help='Input PGN file (.pgn or .pgn.bz2)')
    parser.add_argument('output', help='Output CSV file (.csv or .csv.bz2)')
    args = parser.parse_args()

    games = backend.GamesFile(args.input)
    open_fn = bz2.open if args.output.endswith('.bz2') else open
    mode = 'wt'
    with open_fn(args.output, mode) as f:
        f.write(','.join(full_csv_header) + '\n')
        count = 0
        for _, game_str in games:
            try:
                lines = gameToCSVlines(
                    game_str,
                    with_board_stats=True,
                    allow_non_sf=True,
                )
                for line in lines:
                    f.write(line + '\n')
                count += 1
            except Exception as e:
                backend.printWithDate(f"Skipping game: {e}")
                continue
    backend.printWithDate(f"Wrote {count} games to {args.output}")


if __name__ == '__main__':
    main()
