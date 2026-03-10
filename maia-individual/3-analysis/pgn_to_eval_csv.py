#!/usr/bin/env python3
"""
Converts a PGN file to the minimal CSV format required by prediction_generator.py.
Output columns: game_id, move_ply, move, board, active_player

Usage: python pgn_to_eval_csv.py input.pgn output.csv.bz2 [--player PLAYER]
  --player: optional, filter to only include moves by this player (White/Black username)
"""
import argparse
import bz2
import csv
import io
import sys

try:
    import chess
    import chess.pgn
except ImportError:
    print("Error: chess package required. Install with: pip install python-chess", file=sys.stderr)
    sys.exit(1)


def pgn_to_eval_csv(pgn_path, output_path, target_player=None):
    """Convert PGN to CSV format for prediction_generator."""
    open_fn = bz2.open if pgn_path.endswith('.bz2') else open
    mode = 'rt' if pgn_path.endswith('.bz2') else 'r'

    out_bz2 = output_path.endswith('.bz2')
    out_file = bz2.open(output_path, 'wt') if out_bz2 else open(output_path, 'w', newline='')

    fieldnames = ['game_id', 'move_ply', 'move', 'board', 'active_player']
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    with open_fn(pgn_path, mode, encoding='utf-8', errors='replace') as f:
        pgn_io = f
        if not pgn_path.endswith('.bz2'):
            pgn_io = io.StringIO(f.read())

        game_count = 0
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            game_count += 1
            headers = game.headers
            game_id = headers.get('Site', '').split('/')[-1] or f'game_{game_count}'
            white_player = headers.get('White', '')
            black_player = headers.get('Black', '')

            board = game.board()
            for i, node in enumerate(game.mainline()):
                fen = board.fen()
                is_white = fen.split(' ')[1] == 'w'
                active_player = white_player if is_white else black_player
                if target_player and active_player != target_player:
                    board.push(node.move)
                    continue

                uci_move = node.move.uci()
                writer.writerow({
                    'game_id': game_id,
                    'move_ply': str(i),
                    'move': uci_move,
                    'board': fen,
                    'active_player': active_player,
                })
                board.push(node.move)

    out_file.close()
    print(f"Wrote {game_count} games -> {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert PGN to CSV for prediction_generator evaluation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input', help='Input PGN file (.pgn or .pgn.bz2)')
    parser.add_argument('output', help='Output CSV file (.csv or .csv.bz2)')
    parser.add_argument('--player', help='Only include moves by this player', default=None)
    args = parser.parse_args()
    pgn_to_eval_csv(args.input, args.output, args.player)


if __name__ == '__main__':
    main()
