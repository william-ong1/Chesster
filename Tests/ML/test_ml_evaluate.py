# Tests for ML/evaluate_model.py

import os
import tempfile
from pathlib import Path

import pytest
import torch
import torch.nn as nn

from ML.evaluate_model import EvaluateModel


class LinearModel(nn.Module):
    """Simple model for testing."""

    def __init__(self, in_features: int = 3, out_features: int = 1):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


class TestEvaluateModel:
    """Tests for ML/evaluate_model.py."""

    test_x = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    test_y = torch.tensor([[1.0], [2.0]])

    def test_init(self):
        """Tests EvaluateModel initialization."""
        model = LinearModel(3, 1)
        ev = EvaluateModel(model, self.test_x, self.test_y)
        assert ev.model is model
        assert ev.X.shape == self.test_x.shape
        assert ev.y.shape == self.test_y.shape

    def test_MSE(self):
        """Tests the MSE function."""
        model = LinearModel(3, 1)
        ev = EvaluateModel(model, self.test_x, self.test_y)
        mse = ev.MSE()
        assert mse >= 0
        assert isinstance(mse, (float, torch.Tensor))
        if isinstance(mse, torch.Tensor):
            assert mse.dim() == 0

    def test_MSE_perfect_predictions(self):
        """MSE is 0 when predictions match targets."""
        model = LinearModel(2, 1)
        X = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        y = torch.tensor([[1.0], [2.0]])
        with torch.no_grad():
            model.linear.weight.copy_(torch.tensor([[0.0, 0.5]]))
            model.linear.bias.copy_(torch.tensor(0.0))
        ev = EvaluateModel(model, X, y)
        mse = ev.MSE()
        assert float(mse) == pytest.approx(0.0, abs=1e-5)

    def test_MAE(self):
        """Tests the MAE function."""
        model = LinearModel(3, 1)
        ev = EvaluateModel(model, self.test_x, self.test_y)
        mae = ev.MAE()
        assert mae >= 0
        assert isinstance(mae, (float, torch.Tensor))
        if isinstance(mae, torch.Tensor):
            assert mae.dim() == 0

    def test_MAE_perfect_predictions(self):
        """MAE is 0 when predictions match targets."""
        model = LinearModel(2, 1)
        X = torch.tensor([[1.0, 2.0]])
        y = torch.tensor([[3.0]])
        with torch.no_grad():
            model.linear.weight.copy_(torch.tensor([[0.0, 1.5]]))
            model.linear.bias.copy_(torch.tensor(0.0))
        ev = EvaluateModel(model, X, y)
        mae = ev.MAE()
        assert float(mae) == pytest.approx(0.0, abs=1e-5)

    def test_save_results(self):
        """Tests save_results writes MSE and MAE to file."""
        model = LinearModel(3, 1)
        ev = EvaluateModel(model, self.test_x, self.test_y)
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("model_evals").mkdir(exist_ok=True)
                ev.save_results(0.123, 0.456)
                content = Path("model_evals/results.txt").read_text()
                assert "MSE: 0.123, MAE: 0.456" in content
            finally:
                os.chdir(cwd)

    def test_save_results_appends(self):
        """Tests save_results appends without overwriting."""
        model = LinearModel(3, 1)
        ev = EvaluateModel(model, self.test_x, self.test_y)
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("model_evals").mkdir(exist_ok=True)
                Path("model_evals/results.txt").write_text("existing line\n")
                ev.save_results(1.0, 2.0)
                content = Path("model_evals/results.txt").read_text()
                assert "existing line" in content
                assert "MSE: 1.0, MAE: 2.0" in content
            finally:
                os.chdir(cwd)