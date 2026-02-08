# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Test suite for backend API endpoints

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
sys.path.append('..')

from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager

from backend.api.upload import upload_bp
from backend.api.training import training_bp
from backend.api.agent import agent_bp
from backend.api.auth import auth_bp

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    JWTManager(app)
    
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    app.register_blueprint(agent_bp, url_prefix='/api/agent')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_header(app):
    """Create JWT auth header for testing"""
    with app.app_context():
        access_token = create_access_token(identity='test_user_123')
        return {'Authorization': f'Bearer {access_token}'}

class TestAuthAPI:
    """Tests for authentication endpoints"""
    
    @patch('backend.api.auth.DatabaseManager')
    def test_register_success(self, mock_db, client):
        """Test successful user registration"""
        mock_db.return_value.create_user.return_value = 'user_123'
        
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
    
    @patch('backend.api.auth.DatabaseManager')
    def test_login_success(self, mock_db, client):
        """Test successful login"""
        mock_db.return_value.verify_user.return_value = 'user_123'
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'securepass123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data

class TestUploadAPI:
    """Tests for /api/upload endpoints"""
    
    @patch('backend.api.upload.pgn_to_board_states')
    @patch('backend.api.upload.DatabaseManager')
    def test_upload_valid_pgn(self, mock_db, mock_pgn_convert, client, auth_header):
        """Test uploading valid PGN data"""
        mock_pgn_convert.return_value = {
            'success': True,
            'board_states': [{'fen': 'test', 'move': 'e4'}],
            'metadata': {'white': 'Player1', 'black': 'Player2'}
        }
        mock_db.return_value.insert_game_data.return_value = 'game_123'
        
        response = client.post('/api/upload/pgn', 
            data={'pgn_text': '[Event "Test"]\n1. e4 e5'},
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['games_stored'] > 0
    
    def test_upload_missing_auth(self, client):
        """Test upload without authentication"""
        response = client.post('/api/upload/pgn', 
            data={'pgn_text': '[Event "Test"]\n1. e4 e5'}
        )
        
        assert response.status_code == 401
    
    @patch('backend.api.upload.PGNDownloader')
    def test_import_chess_com(self, mock_downloader, client, auth_header):
        """Test importing from Chess.com"""
        mock_instance = mock_downloader.return_value
        mock_instance.download_chess_com.return_value = {
            'success': True,
            'games': ['pgn1', 'pgn2']
        }
        
        response = client.post('/api/upload/chess-com',
            json={'username': 'testuser', 'months': ['2024/01']},
            headers=auth_header
        )
        
        assert response.status_code == 200

class TestTrainingAPI:
    """Tests for /api/training endpoints"""
    
    @patch('backend.api.training.DatabaseManager')
    @patch('backend.api.training.threading.Thread')
    def test_start_training(self, mock_thread, mock_db, client, auth_header):
        """Test initiating model training"""
        mock_db.return_value.count_user_games.return_value = 50
        mock_db.return_value.create_training_job.return_value = 'job_123'
        
        response = client.post('/api/training/start',
            json={'epochs': 50, 'batch_size': 32, 'learning_rate': 0.001},
            headers=auth_header
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'job_id' in data
        assert mock_thread.called
    
    @patch('backend.api.training.DatabaseManager')
    def test_training_insufficient_data(self, mock_db, client, auth_header):
        """Test training with insufficient games"""
        mock_db.return_value.count_user_games.return_value = 5
        
        response = client.post('/api/training/start',
            json={'epochs': 50},
            headers=auth_header
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Insufficient training data' in data['error']
    
    @patch('backend.api.training.DatabaseManager')
    def test_get_training_status(self, mock_db, client, auth_header):
        """Test polling training status"""
        mock_db.return_value.get_training_status.return_value = {
            'status': 'running',
            'progress': 0.5,
            'current_epoch': 25
        }
        
        response = client.get('/api/training/status/job_123',
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'running'
        assert data['progress'] == 0.5
    
    @patch('backend.api.training.DatabaseManager')
    def test_get_models(self, mock_db, client, auth_header):
        """Test retrieving user's trained models"""
        mock_db.return_value.get_user_models.return_value = [
            {'model_id': 'model1', 'epochs': 50, 'created': '2024-01-01'}
        ]
        
        response = client.get('/api/training/models',
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['models']) > 0

class TestAgentAPI:
    """Tests for /api/agent endpoints"""
    
    @patch('backend.api.agent.Agent')
    @patch('backend.api.agent.ModelCache')
    @patch('backend.api.agent.DatabaseManager')
    def test_get_move_valid_fen(self, mock_db, mock_cache, mock_agent, client, auth_header):
        """Test getting move for valid board state"""
        mock_db.return_value.get_active_model_id.return_value = 'model_123'
        mock_cache.return_value.get.return_value = {'model': Mock()}
        
        mock_move = Mock()
        mock_move.uci.return_value = 'e2e4'
        mock_agent.return_value.get_move.return_value = (mock_move, 0.5)
        
        response = client.post('/api/agent/move',
            json={'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'depth': 3},
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'move' in data
        assert 'evaluation' in data
    
    def test_get_move_invalid_fen(self, client, auth_header):
        """Test that invalid FEN returns error"""
        response = client.post('/api/agent/move',
            json={'fen': 'invalid_fen', 'depth': 3},
            headers=auth_header
        )
        
        assert response.status_code == 400
    
    def test_make_move_valid(self, client, auth_header):
        """Test validating and executing a player move"""
        response = client.post('/api/agent/make-move',
            json={
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'move': 'e2e4'
            },
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'new_fen' in data
        assert 'move_san' in data
    
    def test_make_move_illegal(self, client, auth_header):
        """Test that illegal move is rejected"""
        response = client.post('/api/agent/make-move',
            json={
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'move': 'e2e5'  # Illegal
            },
            headers=auth_header
        )
        
        assert response.status_code == 400
    
    def test_get_legal_moves(self, client, auth_header):
        """Test getting legal moves for a position"""
        response = client.post('/api/agent/legal-moves',
            json={'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'},
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'legal_moves' in data
        assert len(data['legal_moves']) == 20  # 20 legal moves from start
    
    def test_get_legal_moves_for_square(self, client, auth_header):
        """Test getting legal moves for specific square"""
        response = client.post('/api/agent/legal-moves',
            json={
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'square': 'e2'
            },
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['legal_moves']) == 2  # e2e3 and e2e4
