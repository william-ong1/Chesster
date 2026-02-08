# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Test suite for ML components

import pytest
import torch
import chess
import sys
from unittest.mock import Mock, patch, MagicMock
sys.path.append('..')

from ML.state_encoder import StateEncoder
from ML.model_cache import ModelCache
from ML.agent import Agent
from ML.model_architectures.three_layer_nn import ThreeLayerNN
from ML.chess_dataset import ChessDataset

class TestStateEncoder:
    """Tests for board state encoding"""
    
    def test_encode_starting_position(self):
        """Test encoding the starting chess position"""
        encoder = StateEncoder()
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        tensor = encoder.encode_board(starting_fen)
        
        # Check shape: 14 channels (12 pieces + 2 metadata), 8x8 board
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
    
    def test_decode_position(self):
        """Test decoding tensor back to FEN"""
        encoder = StateEncoder()
        original_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        tensor = encoder.encode_board(original_fen)
        decoded_fen = encoder.decode_board(tensor)
        
        # Board position should match (metadata may differ slightly)
        assert decoded_fen.split()[0] == original_fen.split()[0]

class TestModelCache:
    """Tests for model caching"""
    
    def test_cache_put_and_get(self):
        """Test adding and retrieving models"""
        cache = ModelCache(max_size=2)
        
        # Create dummy model
        model = ThreeLayerNN()
        model_id = 'test_model_1'
        metadata = {'epochs': 50, 'accuracy': 0.85}
        
        cache.put(model_id, model, metadata)
        cached_data = cache.get(model_id)
        
        assert cached_data is not None
        assert cached_data['metadata']['epochs'] == 50
    
    def test_cache_eviction(self):
        """Test that cache evicts oldest entries when full"""
        cache = ModelCache(max_size=2)
        
        model1 = ThreeLayerNN()
        model2 = ThreeLayerNN()
        model3 = ThreeLayerNN()
        
        cache.put('model1', model1, {})
        cache.put('model2', model2, {})
        cache.put('model3', model3, {})  # Should evict model1
        
        assert cache.get('model1') is None
        assert cache.get('model2') is not None
        assert cache.get('model3') is not None

class TestChessDataset:
    """Tests for chess dataset"""
    
    def test_dataset_creation(self):
        """Test creating dataset from game data"""
        game_data = [
            {
                'board_states': [
                    {'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 
                     'move': 'e2e4', 'evaluation': 0.3},
                    {'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1', 
                     'move': 'e7e5', 'evaluation': 0.2}
                ]
            }
        ]
        
        dataset = ChessDataset(game_data)
        
        assert len(dataset) == 2
        
        # Get first item
        state, move_idx, eval_score = dataset[0]
        assert state.shape == (14, 8, 8)
        assert isinstance(move_idx, int)
        assert isinstance(eval_score, float)

class TestThreeLayerNN:
    """Tests for 3-layer neural network architecture"""
    
    def test_model_forward_pass(self):
        """Test forward pass through model"""
        model = ThreeLayerNN()
        
        # Create dummy input (batch_size=2, channels=14, height=8, width=8)
        input_tensor = torch.randn(2, 14, 8, 8)
        
        output = model(input_tensor)
        
        # Output should be (batch_size, num_possible_moves)
        assert output.shape[0] == 2
        assert output.shape[1] > 0  # Should have move predictions
    
    def test_model_trainable(self):
        """Test that model parameters are trainable"""
        model = ThreeLayerNN()
        
        # Check that model has trainable parameters
        params = list(model.parameters())
        assert len(params) > 0
        assert all(p.requires_grad for p in params)

class TestAgent:
    """Tests for chess agent"""
    
    def test_agent_get_move(self):
        """Test agent move generation"""
        model = ThreeLayerNN()
        agent = Agent(model, depth=2)
        
        board = chess.Board()  # Starting position
        
        move, evaluation = agent.get_move(board)
        
        assert move is not None
        assert move in board.legal_moves
        assert isinstance(evaluation, (int, float))
    
    def test_agent_evaluate_position(self):
        """Test position evaluation"""
        model = ThreeLayerNN()
        agent = Agent(model, depth=1)
        
        board = chess.Board()
        evaluation = agent._evaluate_position(board)
        
        assert isinstance(evaluation, (int, float))
    
    @patch.object(Agent, '_evaluate_position')
    def test_alpha_beta_search(self, mock_eval):
        """Test alpha-beta pruning"""
        mock_eval.return_value = 0.5
        
        model = ThreeLayerNN()
        agent = Agent(model, depth=3)
        board = chess.Board()
        
        move, score = agent.get_move(board)
        
        assert move is not None
        # Alpha-beta should have been called
        assert mock_eval.called
