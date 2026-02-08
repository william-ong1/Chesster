# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Test suite for ML components

import pytest
import torch
import sys
sys.path.append('..')

from ML.state_encoder import StateEncoder
from ML.model_cache import ModelCache

class TestStateEncoder:
    """Tests for board state encoding"""
    
    def test_encode_starting_position(self):
        """Test encoding the starting chess position"""
        encoder = StateEncoder()
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        tensor = encoder.encode_board(starting_fen)
        
        # Check shape: 14 channels, 8x8 board
        assert tensor.shape == (14, 8, 8)
        
        # Check that pieces are encoded (some channels should have values)
        assert tensor.sum() > 0
    
    def test_encode_batch(self):
        """Test encoding multiple positions"""
        encoder = StateEncoder()
        fens = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        ]
        
        batch_tensor = encoder.encode_batch(fens)
        
        assert batch_tensor.shape == (2, 14, 8, 8)

class TestModelCache:
    """Tests for model caching"""
    
    def test_cache_put_and_get(self):
        """Test adding and retrieving models"""
        cache = ModelCache(capacity=2)
        
        # Create dummy models
        model1 = torch.nn.Linear(10, 10)
        model2 = torch.nn.Linear(10, 10)
        
        # Add to cache
        cache.put("model1", model1)
        cache.put("model2", model2)
        
        # Retrieve
        retrieved = cache.get("model1")
        assert retrieved is model1
    
    def test_cache_eviction(self):
        """Test LRU eviction when capacity exceeded"""
        cache = ModelCache(capacity=2)
        
        model1 = torch.nn.Linear(10, 10)
        model2 = torch.nn.Linear(10, 10)
        model3 = torch.nn.Linear(10, 10)
        
        cache.put("model1", model1)
        cache.put("model2", model2)
        cache.put("model3", model3)  # Should evict model1
        
        assert cache.get("model1") is None
        assert cache.get("model2") is model2
        assert cache.get("model3") is model3
