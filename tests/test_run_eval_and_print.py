"""Tests for maia-individual/3-analysis/run_eval_and_print.py evaluation logic."""
# pylint: disable=redefined-outer-name

import bz2
import csv
import io
import sys
import tempfile
import warnings
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import unittest
from unittest import mock, TestCase

# Suppress third-party deprecation warnings (e.g. dateutil) during test run
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add maia-individual/3-analysis to path so we can import run_eval_and_print
MAIA_ANALYSIS = Path(__file__).resolve().parent.parent / "maia-individual" / "3-analysis"
sys.path.insert(0, str(MAIA_ANALYSIS))


def create_eval_csv(model_correct_values):
    """Create a bz2 CSV matching prediction_generator output format."""
    headers = [
        "game_id", "move_ply", "player_move", "model_move", "model_v", "model_correct",
        "model_name", "model_display_name", "player_name", "rl_depth", "top_p", "act_p",
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore")
    w.writeheader()
    for i, correct in enumerate(model_correct_values):
        w.writerow({
            "game_id": f"g{i}",
            "move_ply": i,
            "player_move": "e2e4",
            "model_move": "e2e4" if correct else "e7e5",
            "model_correct": correct,
            "model_name": "test",
            "player_name": "test_player",
        })
    return bz2.compress(buf.getvalue().encode("utf-8"))


class TestRunEvalAndPrint(TestCase):
    """Test evaluation logic and output formatting."""

    def test_computes_accuracy_from_white_csv(self):
        """Accuracy is computed correctly from model_correct column."""
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp)
            username = "test_player"
            (session_dir / username / "csvs").mkdir(parents=True)
            (session_dir / username / "csvs" / "test_white.csv.bz2").write_bytes(b"dummy")
            # Only white - so we only process white and don't need eval_black

            # Pre-create eval output (as if prediction_generator had run)
            eval_data = create_eval_csv([True, True, True, False])
            (session_dir / "eval_white.csv.bz2").write_bytes(eval_data)

            with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0)):
                from run_eval_and_print import main

                with mock.patch(
                    "sys.argv",
                    ["run_eval_and_print.py", "/fake/model", str(session_dir), username],
                ):
                    buf = io.StringIO()
                    err_buf = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err_buf):
                        main()
                    out = buf.getvalue()

            self.assertIn("Test accuracy (white): 75.00%", out)
            self.assertIn("Overall test accuracy: 75.00%", out)
            self.assertIn("=== EVALUATION COMPLETE ===", out)

    def test_combines_white_and_black_accuracy(self):
        """Overall accuracy is weighted average when both colors present."""
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp)
            username = "test_player"
            (session_dir / username / "csvs").mkdir(parents=True)
            (session_dir / username / "csvs" / "test_white.csv.bz2").write_bytes(b"dummy")
            (session_dir / username / "csvs" / "test_black.csv.bz2").write_bytes(b"dummy")

            (session_dir / "eval_white.csv.bz2").write_bytes(
                create_eval_csv([True, False, True, False])
            )
            (session_dir / "eval_black.csv.bz2").write_bytes(
                create_eval_csv([True, True, True])
            )

            with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0)):
                from run_eval_and_print import main

                with mock.patch(
                    "sys.argv",
                    ["run_eval_and_print.py", "/fake/model", str(session_dir), username],
                ):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        main()
                    out = buf.getvalue()

            self.assertIn("Test accuracy (white): 50.00%", out)
            self.assertIn("Test accuracy (black): 100.00%", out)
            self.assertIn("Overall test accuracy: 71.43%", out)

    def test_skips_missing_test_csv(self):
        """When no test CSVs exist, prints skip message to stderr."""
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp)
            username = "nobody"
            (session_dir / username / "csvs").mkdir(parents=True)

            with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0)):
                from run_eval_and_print import main

                with mock.patch(
                    "sys.argv",
                    ["run_eval_and_print.py", "/fake/model", str(session_dir), username],
                ):
                    buf = io.StringIO()
                    with redirect_stderr(buf):
                        main()
                    err = buf.getvalue()

            self.assertTrue("Skipping" in err or "No test CSVs" in err)


if __name__ == "__main__":
    unittest.main()
