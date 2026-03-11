#!/usr/bin/env python3
"""Run prediction_generator on test CSVs and print accuracy to stdout."""

import argparse
import os
import subprocess
import sys

import pandas

# Add maia-individual root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
maia_root = os.path.dirname(script_dir)
sys.path.insert(0, maia_root)


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate model on test set and print accuracy'
    )
    parser.add_argument('model', help='Path to model .pb.gz or directory')
    parser.add_argument(
        'session_dir', help='Session directory (contains username/csvs/)'
    )
    parser.add_argument('username', help='Player username')
    args = parser.parse_args()

    player_dir = os.path.join(args.session_dir, args.username, 'csvs')
    results = []
    for color in ['white', 'black']:
        csv_path = os.path.join(player_dir, f'test_{color}.csv.bz2')
        if not os.path.isfile(csv_path):
            msg = f'[Eval] Skipping {color}: test CSV not found at {csv_path}'
            print(msg, file=sys.stderr)
            continue
        out_path = os.path.join(args.session_dir, f'eval_{color}.csv.bz2')
        try:
            pred_gen = os.path.join(
                maia_root, '3-analysis', 'prediction_generator.py'
            )
            subprocess.run([
                sys.executable,
                pred_gen,
                '--target_player', args.username,
                '--overwrite',
                args.model,
                csv_path,
                out_path,
            ], check=True, capture_output=True)
            df = pandas.read_csv(out_path, low_memory=False)
            acc = float(df['model_correct'].mean())
            n = len(df)
            results.append((color, acc, n))
            print(f'Test accuracy ({color}): {acc:.2%} (n={n})')
        except subprocess.CalledProcessError as exc:
            msg = f'[Eval] prediction_generator failed for {color}: {exc}'
            print(msg, file=sys.stderr)
            raise

    if results:
        total_n = sum(r[2] for r in results)
        overall = sum(r[1] * r[2] for r in results) / total_n if total_n else 0
        print(f'Overall test accuracy: {overall:.2%} (n={total_n})')
        print('=== EVALUATION COMPLETE ===')
    else:
        print(
            '[Eval] No test CSVs found - skipping evaluation',
            file=sys.stderr
        )


if __name__ == '__main__':
    main()
