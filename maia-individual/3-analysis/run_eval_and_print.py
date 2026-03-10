#!/usr/bin/env python3
"""Run prediction_generator on test CSVs and print accuracy to stdout."""

import argparse
import os
import subprocess
import sys

# Add maia-individual root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
maia_root = os.path.dirname(script_dir)
sys.path.insert(0, maia_root)


def main():
    parser = argparse.ArgumentParser(description='Evaluate model on test set and print accuracy')
    parser.add_argument('model', help='Path to model .pb.gz or directory')
    parser.add_argument('session_dir', help='Session directory (contains username/csvs/)')
    parser.add_argument('username', help='Player username')
    args = parser.parse_args()

    import pandas as p

    player_dir = os.path.join(args.session_dir, args.username, 'csvs')
    results = []
    for color in ['white', 'black']:
        csv_path = os.path.join(player_dir, f'test_{color}.csv.bz2')
        if not os.path.isfile(csv_path):
            print(f'[Eval] Skipping {color}: test CSV not found at {csv_path}', file=sys.stderr)
            continue
        out_path = os.path.join(args.session_dir, f'eval_{color}.csv.bz2')
        try:
            subprocess.run([
                sys.executable,
                os.path.join(maia_root, '3-analysis', 'prediction_generator.py'),
                '--target_player', args.username,
                '--overwrite',
                args.model,
                csv_path,
                out_path,
            ], check=True, capture_output=True)
            df = p.read_csv(out_path, low_memory=False)
            acc = float(df['model_correct'].mean())
            n = len(df)
            results.append((color, acc, n))
            print(f'Test accuracy ({color}): {acc:.2%} (n={n})')
        except subprocess.CalledProcessError as e:
            print(f'[Eval] prediction_generator failed for {color}: {e}', file=sys.stderr)
            raise

    if results:
        total_n = sum(r[2] for r in results)
        overall = sum(r[1] * r[2] for r in results) / total_n if total_n else 0
        print(f'Overall test accuracy: {overall:.2%} (n={total_n})')
        print('=== EVALUATION COMPLETE ===')
    else:
        print('[Eval] No test CSVs found - skipping evaluation', file=sys.stderr)


if __name__ == '__main__':
    main()
