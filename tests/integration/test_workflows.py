# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Integration tests for cross-component workflows

import pytest
import sys
import time
from unittest.mock import Mock, patch, MagicMock
sys.path.append('..')

from data.PGN_cleaner import clean_pgn
from data.PGN_to_board_state import pgn_to_board_states
from data.database_manager import DatabaseManager
from ML.agent import Agent
from ML.model_architectures.three_layer_nn import ThreeLayerNN
from ML.chess_dataset import ChessDataset
import chess

class TestEndToEndWorkflow:
    """Tests for complete user workflows"""
    
    @patch('data.database_manager.MongoClient')
    def test_upload_train_play_workflow(self, mock_mongo):
        """Test complete workflow: Upload PGN -> Train Model -> Play Game"""
        
        # Step 1: Upload PGN game
        sample_pgn = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O 1-0"""
        
        cleaned_pgn = clean_pgn(sample_pgn)
        result = pgn_to_board_states(cleaned_pgn)
        
        assert result['success'] == True
        assert len(result['board_states']) > 0
        
        # Step 2: Store in database
        mock_db = MagicMock()
        mock_mongo.return_value = {'chesster': mock_db}
        
        db_manager = DatabaseManager()
        game_id = db_manager.insert_game_data(
            'test_user',
            result['metadata'],
            result['board_states']
        )
        
        assert game_id is not None
        
        # Step 3: Retrieve for training
        mock_db.games.find.return_value = [
            {'board_states': result['board_states']}
        ]
        
        games = db_manager.get_user_games('test_user', limit=10)
        assert len(games) > 0
        
        # Step 4: Create dataset
        dataset = ChessDataset(games)
        assert len(dataset) > 0
        
        # Step 5: Use trained model for gameplay
        model = ThreeLayerNN()
        agent = Agent(model, depth=2)
        
        board = chess.Board()
        move, evaluation = agent.get_move(board)
        
        assert move is not None
        assert move in board.legal_moves

class TestDataPipelineToMLIntegration:
    """Tests for data pipeline -> ML pipeline integration"""
    
    def test_pgn_to_dataset_pipeline(self):
        """Test converting PGN to training dataset"""
        # Multiple games
        games_pgn = [
            """[Event "Game 1"]
1. e4 e5 2. Nf3""",
            """[Event "Game 2"]
1. d4 d5 2. c4"""
        ]
        
        all_board_states = []
        for pgn in games_pgn:
            result = pgn_to_board_states(pgn)
            if result['success']:
                all_board_states.extend(result['board_states'])
        
        # Create dataset from board states
        game_data = [{'board_states': all_board_states}]
        dataset = ChessDataset(game_data)
        
        assert len(dataset) > 0
        
        # Verify dataset items are properly formatted
        state, move_idx, eval_score = dataset[0]
        assert state.shape == (14, 8, 8)
        assert isinstance(move_idx, int)

class TestBackendToFrontendIntegration:
    """Tests for backend API -> frontend integration"""
    
    @patch('backend.api.agent.Agent')
    @patch('backend.api.agent.ModelCache')
    @patch('backend.api.agent.DatabaseManager')
    def test_agent_api_workflow(self, mock_db, mock_cache, mock_agent):
        """Test agent API returns valid moves for frontend"""
        from flask import Flask
        from backend.api.agent import agent_bp
        from flask_jwt_extended import JWTManager, create_access_token
        
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test'
        JWTManager(app)
        app.register_blueprint(agent_bp, url_prefix='/api/agent')
        
        mock_db.return_value.get_active_model_id.return_value = 'model_123'
        mock_cache.return_value.get.return_value = {'model': Mock()}
        
        mock_move = Mock()
        mock_move.uci.return_value = 'e2e4'
        mock_agent.return_value.get_move.return_value = (mock_move, 0.5)
        
        with app.test_client() as client:
            with app.app_context():
                token = create_access_token(identity='test_user')
            
            # Request bot move
            response = client.post('/api/agent/move',
                json={'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.json
            assert 'move' in data
            assert 'evaluation' in data
            
            # Make player move
            response = client.post('/api/agent/make-move',
                json={'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'move': 'e2e4'},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.json
            assert 'new_fen' in data
            assert 'move_san' in data

class TestTrainingPipeline:
    """Tests for complete training pipeline"""
    
    @patch('backend.api.training.DatabaseManager')
    def test_training_job_creation_and_status(self, mock_db):
        """Test creating training job and checking status"""
        from flask import Flask
        from backend.api.training import training_bp
        from flask_jwt_extended import JWTManager, create_access_token
        
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test'
        JWTManager(app)
        app.register_blueprint(training_bp, url_prefix='/api/training')
        
        mock_db.return_value.count_user_games.return_value = 50
        mock_db.return_value.create_training_job.return_value = 'job_123'
        
        with app.test_client() as client:
            with app.app_context():
                token = create_access_token(identity='test_user')
            
            # Start training
            response = client.post('/api/training/start',
                json={'epochs': 50, 'batch_size': 32},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 201
            data = response.json
            assert 'job_id' in data
            
            # Check status
            mock_db.return_value.get_training_status.return_value = {
                'status': 'running',
                'progress': 0.5,
                'current_epoch': 25
            }
            
            response = client.get(f'/api/training/status/{data["job_id"]}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            status_data = response.json
            assert status_data['status'] == 'running'
            assert status_data['progress'] == 0.5

class TestGamePlayWorkflow:
    """Tests for complete game play workflow"""
    
    def test_complete_game_sequence(self):
        """Test a sequence of moves in a game"""
        model = ThreeLayerNN()
        agent = Agent(model, depth=2)
        
        board = chess.Board()
        moves_made = []
        
        # Play first 5 moves
        for _ in range(5):
            if board.is_game_over():
                break
            
            move, eval_score = agent.get_move(board)
            assert move in board.legal_moves
            
            board.push(move)
            moves_made.append(move.uci())
        
        assert len(moves_made) > 0
        assert len(moves_made) <= 5

class TestErrorHandling:
    """Tests for error handling across components"""
    
    def test_invalid_pgn_handling(self):
        """Test that invalid PGN is handled gracefully"""
        invalid_pgn = "This is not a valid PGN"
        
        result = pgn_to_board_states(invalid_pgn)
        assert result['success'] == False
        assert 'error' in result
    
    def test_invalid_fen_handling(self):
        """Test that invalid FEN is handled gracefully"""
        model = ThreeLayerNN()
        agent = Agent(model, depth=2)
        
        try:
            board = chess.Board("invalid_fen")
            move, eval_score = agent.get_move(board)
            assert False, "Should have raised exception"
        except ValueError:
            pass  # Expected
