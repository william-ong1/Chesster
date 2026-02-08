# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# API endpoints for model training
# Handles training job creation, progress tracking, and model management

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import threading
import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from data.database_manager import DatabaseManager
from ML.model_architectures.three_layer_nn import ThreeLayerNN
# from ML.chess_dataset import ChessDataset  # Will be implemented
# from ML.training import Training  # Will be implemented

training_bp = Blueprint('training', __name__)

# Initialize database manager
db = DatabaseManager()

# Architecture registry
ARCHITECTURES = {
    '3_layer_nn': ThreeLayerNN,
    'three_layer_nn': ThreeLayerNN
}

def run_training_job(job_id: str, user_id: str, architecture: str, config: dict):
    """
    Background training function (runs in separate thread)
    
    Args:
        job_id: Training job identifier
        user_id: User identifier
        architecture: Architecture class name
        config: Training configuration dict
    """
    try:
        print(f"🚀 Starting training job: {job_id}")
        
        # Update status to running
        db.update_training_status(job_id, "running", progress=0)
        
        # Load user's game data
        games = db.get_user_games(user_id, limit=10000)
        
        if not games:
            db.update_training_status(
                job_id, "failed",
                error="No game data found for user"
            )
            return
        
        print(f"📊 Loaded {len(games)} games for training")
        
        # TODO: Create ChessDataset and DataLoader
        # For now, simulate training progress
        
        # Get architecture class
        arch_class = ARCHITECTURES.get(architecture)
        if not arch_class:
            db.update_training_status(
                job_id, "failed",
                error=f"Unknown architecture: {architecture}"
            )
            return
        
        # Initialize model
        model = arch_class()
        
        # Simulate training epochs
        epochs = config.get('epochs', 50)
        
        for epoch in range(1, epochs + 1):
            # TODO: Implement actual training loop
            # For now, simulate progress
            
            progress = epoch / epochs
            current_loss = 1.0 - (progress * 0.8)  # Simulated loss decrease
            
            # Update progress every 5 epochs
            if epoch % 5 == 0 or epoch == epochs:
                db.update_training_status(
                    job_id, "running",
                    progress=progress,
                    current_epoch=epoch
                )
                print(f"📈 Epoch {epoch}/{epochs}, Loss: {current_loss:.4f}")
        
        # Save trained model
        model_name = f"{architecture}_epoch{epochs}"
        metadata = {
            'epochs': epochs,
            'final_loss': current_loss,
            'training_games': len(games),
            'config': config
        }
        
        model_id = db.save_model(
            user_id=user_id,
            model_name=model_name,
            model_state=model.state_dict(),
            architecture=architecture,
            metadata=metadata
        )
        
        if not model_id:
            db.update_training_status(
                job_id, "failed",
                error="Failed to save model to database"
            )
            return
        
        # Set as active model
        db.set_active_model(user_id, model_id)
        
        # Mark job as completed
        db.update_training_status(
            job_id, "completed",
            progress=1.0,
            current_epoch=epochs,
            model_id=model_id
        )
        
        print(f"✅ Training job completed: {job_id} -> {model_id}")
        
    except Exception as e:
        print(f"❌ Training job failed: {e}")
        db.update_training_status(
            job_id, "failed",
            error=str(e)
        )

@training_bp.route('/start', methods=['POST'])
@jwt_required()
def start_training():
    """
    Start a new training job
    
    Request body:
        {
            "architecture": str (optional, default: "3_layer_nn"),
            "epochs": int (optional, default: 50),
            "batch_size": int (optional, default: 64),
            "learning_rate": float (optional, default: 0.001)
        }
    
    Returns:
        201: {
            "success": true,
            "job_id": str,
            "estimated_time_minutes": int
        }
        
        400: {"error": str} - Validation error
        401: {"error": str} - Unauthorized
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Parse request
        data = request.get_json() or {}
        
        architecture = data.get('architecture', '3_layer_nn')
        epochs = data.get('epochs', 50)
        batch_size = data.get('batch_size', 64)
        learning_rate = data.get('learning_rate', 0.001)
        
        # Validation
        if architecture not in ARCHITECTURES:
            return jsonify({
                "error": f"Unknown architecture: {architecture}. Available: {list(ARCHITECTURES.keys())}"
            }), 400
        
        if epochs < 1 or epochs > 1000:
            return jsonify({"error": "epochs must be between 1 and 1000"}), 400
        
        if batch_size < 1 or batch_size > 512:
            return jsonify({"error": "batch_size must be between 1 and 512"}), 400
        
        # Check if user has sufficient game data
        game_count = db.count_user_games(user_id)
        
        if game_count < 10:
            return jsonify({
                "error": f"Insufficient training data. Have {game_count} games, need at least 10."
            }), 400
        
        print(f"🎯 User {user_id} has {game_count} games for training")
        
        # Create training configuration
        config = {
            'architecture': architecture,
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate
        }
        
        # Create training job in database
        job_id = db.create_training_job(user_id, config)
        
        # Start training in background thread
        training_thread = threading.Thread(
            target=run_training_job,
            args=(job_id, user_id, architecture, config),
            daemon=True
        )
        training_thread.start()
        
        # Estimate training time (rough estimate: 30 seconds per epoch)
        estimated_minutes = max(1, (epochs * 30) // 60)
        
        print(f"✅ Training job started: {job_id}")
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "estimated_time_minutes": estimated_minutes
        }), 201
        
    except Exception as e:
        print(f"❌ Start training error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@training_bp.route('/status/<job_id>', methods=['GET'])
@jwt_required()
def get_training_status(job_id: str):
    """
    Get training job status and progress
    
    Path parameters:
        job_id: Training job identifier
    
    Returns:
        200: {
            "job_id": str,
            "status": str (pending, running, completed, failed),
            "progress": float (0.0 to 1.0),
            "current_epoch": int,
            "total_epochs": int,
            "created_at": str,
            "started_at": str,
            "completed_at": str,
            "model_id": str (if completed),
            "error": str (if failed)
        }
        
        401: {"error": str} - Unauthorized
        404: {"error": str} - Job not found
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Retrieve training job
        job = db.get_training_job(job_id)
        
        if not job:
            return jsonify({"error": "Training job not found"}), 404
        
        # Verify user owns this job
        if job['user_id'] != user_id:
            return jsonify({"error": "Unauthorized access to training job"}), 403
        
        # Prepare response
        response = {
            "job_id": job['job_id'],
            "status": job['status'],
            "progress": job.get('progress', 0),
            "current_epoch": job.get('current_epoch', 0),
            "total_epochs": job.get('total_epochs', 0),
            "created_at": job['created_at'].isoformat()
        }
        
        if job.get('started_at'):
            response['started_at'] = job['started_at'].isoformat()
        
        if job.get('completed_at'):
            response['completed_at'] = job['completed_at'].isoformat()
        
        if job.get('model_id'):
            response['model_id'] = job['model_id']
        
        if job.get('error'):
            response['error'] = job['error']
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Get training status error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@training_bp.route('/models', methods=['GET'])
@jwt_required()
def get_user_models():
    """
    Get all trained models for current user
    
    Returns:
        200: {
            "models": [{
                "model_id": str,
                "model_name": str,
                "architecture": str,
                "created_at": str,
                "size_bytes": int,
                "metadata": dict,
                "is_active": bool
            }]
        }
        
        401: {"error": str} - Unauthorized
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Get active model ID
        active_model_id = db.get_active_model_id(user_id)
        
        # Retrieve user's models
        models = db.get_user_models(user_id)
        
        # Format response
        model_list = []
        for model in models:
            model_data = {
                "model_id": model['model_id'],
                "model_name": model['model_name'],
                "architecture": model['architecture'],
                "created_at": model['created_at'].isoformat(),
                "size_bytes": model.get('size_bytes', 0),
                "metadata": model.get('metadata', {}),
                "is_active": model['model_id'] == active_model_id
            }
            model_list.append(model_data)
        
        return jsonify({"models": model_list}), 200
        
    except Exception as e:
        print(f"❌ Get user models error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@training_bp.route('/models/<model_id>/activate', methods=['POST'])
@jwt_required()
def activate_model(model_id: str):
    """
    Set a model as the active model for gameplay
    
    Path parameters:
        model_id: Model identifier to activate
    
    Returns:
        200: {
            "success": true,
            "model_id": str,
            "message": str
        }
        
        401: {"error": str} - Unauthorized
        404: {"error": str} - Model not found
        500: {"error": str} - Server error
    """
    try:
        # Get user_id from JWT
        user_id = get_jwt_identity()
        
        # Verify model exists and belongs to user
        models = db.get_user_models(user_id)
        model_ids = [m['model_id'] for m in models]
        
        if model_id not in model_ids:
            return jsonify({"error": "Model not found or unauthorized"}), 404
        
        # Set as active model
        success = db.set_active_model(user_id, model_id)
        
        if not success:
            return jsonify({"error": "Failed to activate model"}), 500
        
        print(f"✅ Activated model {model_id} for user {user_id}")
        
        return jsonify({
            "success": True,
            "model_id": model_id,
            "message": "Model activated successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Activate model error: {e}")
        return jsonify({"error": "Internal server error"}), 500
