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
    found_any_test_csv = False
    for color in ['white', 'black']:
        csv_path = os.path.join(player_dir, f'test_{color}.csv.bz2')
        if not os.path.isfile(csv_path):
            msg = f'[Eval] Skipping {color}: test CSV not found at {csv_path}'
            print(msg, file=sys.stderr)
            continue
        found_any_test_csv = True

        # Check if input has data (avoid running on empty test set)
        try:
            df_in = pandas.read_csv(csv_path, nrows=5, low_memory=False)
            if len(df_in) == 0:
                msg = f'[Eval] Skipping {color}: test CSV is empty'
                print(msg, file=sys.stderr)
                continue
        except Exception:  # pylint: disable=broad-except
            pass  # Proceed; prediction_generator will surface the error

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
            n = len(df)
            if n == 0:
                msg = (
                    f'[Eval] {color}: 0 positions evaluated. '
                    f'Check that test CSV has rows with active_player='
                    f'"{args.username}"'
                )
                print(msg, file=sys.stderr)
                print(f'Test accuracy ({color}): N/A (n=0)', file=sys.stderr)
                continue
            acc = float(df['model_correct'].mean())
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
    elif found_any_test_csv:
        print(
            '[Eval] Test CSVs found but evaluation produced no data. '
            'Possible causes: test set too small, or active_player '
            'in CSV does not match username.',
            file=sys.stderr
        )
    else:
        print(
            '[Eval] No test CSVs found - skipping evaluation',
            file=sys.stderr
        )


if __name__ == '__main__':
    main()
