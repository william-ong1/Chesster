# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Database manager for MongoDB operations
# Handles user management, game storage, and model persistence

from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime
from typing import Optional, Dict, List, Any
import torch
import io
import os

class DatabaseManager:
    """
    Manages all MongoDB database operations for Chesster.
    
    Collections:
    - users: User accounts and authentication
    - game_data: Chess games and board states
    - models: Model metadata
    - training_jobs: Training status tracking
    
    GridFS:
    - Used for storing model binaries >16MB
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: MongoDB connection URI (defaults to env var)
        """
        # Get connection string from environment or use default
        if connection_string is None:
            connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        # Connect to MongoDB
        self.client = MongoClient(connection_string)
        self.db = self.client['chesster']
        
        # Initialize GridFS for large model storage
        self.fs = GridFS(self.db)
        
        # Collections
        self.users = self.db['users']
        self.game_data = self.db['game_data']
        self.models = self.db['models']
        self.training_jobs = self.db['training_jobs']
        
        print(f"✅ DatabaseManager initialized: {connection_string}")
    
    # ==================== User Management ====================
    
    def create_user(self, user_id: str, username: str, email: str, password_hash: str) -> bool:
        """
        Create a new user account
        
        Args:
            user_id: Unique user identifier
            username: Username (must be unique)
            email: Email address (must be unique)
            password_hash: Hashed password (use werkzeug.security.generate_password_hash)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            user_doc = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "active_model_id": None,
                "stats": {
                    "games_uploaded": 0,
                    "models_trained": 0,
                    "games_played": 0
                }
            }
            
            self.users.insert_one(user_doc)
            print(f"✅ User created: {username} ({user_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by user_id
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            User document or None if not found
        """
        return self.users.find_one({"user_id": user_id})
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by username
        
        Args:
            username: Username to search for
        
        Returns:
            User document or None if not found
        """
        return self.users.find_one({"username": username})
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by email
        
        Args:
            email: Email address to search for
        
        Returns:
            User document or None if not found
        """
        return self.users.find_one({"email": email.lower()})
    
    def update_last_login(self, user_id: str) -> bool:
        """
        Update last login timestamp for user
        
        Args:
            user_id: User identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating last login: {e}")
            return False
    
    def update_user_stats(self, user_id: str, stat_name: str, increment: int = 1) -> bool:
        """
        Increment user statistics
        
        Args:
            user_id: User identifier
            stat_name: Name of stat to increment (games_uploaded, models_trained, games_played)
            increment: Amount to increment by (default 1)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {"$inc": {f"stats.{stat_name}": increment}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating user stats: {e}")
            return False
    
    # ==================== Game Data Management ====================
    
    def insert_game_data(self, user_id: str, game_metadata: Dict[str, Any], 
                        board_states: List[Dict[str, Any]]) -> Optional[str]:
        """
        Insert game data with board states
        
        Args:
            user_id: User who owns this game
            game_metadata: Metadata dict (event, white, black, result, etc.)
            board_states: List of board state dicts with FEN, move, eval
        
        Returns:
            Inserted document ID or None on error
        """
        try:
            game_doc = {
                "user_id": user_id,
                "metadata": game_metadata,
                "board_states": board_states,
                "uploaded_at": datetime.utcnow(),
                "num_moves": len(board_states)
            }
            
            result = self.game_data.insert_one(game_doc)
            
            # Update user stats
            self.update_user_stats(user_id, "games_uploaded")
            
            print(f"✅ Game data inserted: {result.inserted_id} ({len(board_states)} moves)")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error inserting game data: {e}")
            return None
    
    def get_user_games(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve games for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of games to return
        
        Returns:
            List of game documents
        """
        return list(self.game_data.find({"user_id": user_id}).limit(limit))
    
    def count_user_games(self, user_id: str) -> int:
        """
        Count total games for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of games
        """
        return self.game_data.count_documents({"user_id": user_id})
    
    # ==================== Model Management ====================
    
    def save_model(self, user_id: str, model_name: str, model_state: Dict[str, torch.Tensor],
                   architecture: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Save trained model to database (uses GridFS for large models)
        
        Args:
            user_id: User who owns the model
            model_name: Name for the model
            model_state: Model state_dict from torch
            architecture: Architecture class name (e.g., "ThreeLayerNN")
            metadata: Training metadata (epochs, loss, accuracy, etc.)
        
        Returns:
            Model ID or None on error
        """
        try:
            # Serialize model state to bytes
            buffer = io.BytesIO()
            torch.save(model_state, buffer)
            model_bytes = buffer.getvalue()
            
            # Store in GridFS if >16MB, otherwise store directly
            if len(model_bytes) > 16 * 1024 * 1024:
                # Use GridFS for large models
                file_id = self.fs.put(
                    model_bytes,
                    filename=f"{user_id}_{model_name}.pt",
                    user_id=user_id,
                    model_name=model_name
                )
                storage_type = "gridfs"
                model_data = None
                gridfs_id = file_id
            else:
                # Store directly in document
                storage_type = "inline"
                model_data = model_bytes
                gridfs_id = None
            
            # Create model metadata document
            model_doc = {
                "model_id": f"model_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "model_name": model_name,
                "architecture": architecture,
                "storage_type": storage_type,
                "model_data": model_data,
                "gridfs_id": gridfs_id,
                "metadata": metadata,
                "created_at": datetime.utcnow(),
                "size_bytes": len(model_bytes)
            }
            
            result = self.models.insert_one(model_doc)
            model_id = model_doc["model_id"]
            
            # Update user stats
            self.update_user_stats(user_id, "models_trained")
            
            print(f"✅ Model saved: {model_id} ({storage_type}, {len(model_bytes)} bytes)")
            return model_id
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return None
    
    def load_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Load model from database
        
        Args:
            model_id: Model identifier
        
        Returns:
            Dict with 'state_dict', 'architecture', 'metadata' or None on error
        """
        try:
            # Retrieve model metadata
            model_doc = self.models.find_one({"model_id": model_id})
            
            if not model_doc:
                print(f"❌ Model not found: {model_id}")
                return None
            
            # Load model bytes
            if model_doc["storage_type"] == "gridfs":
                # Load from GridFS
                file = self.fs.get(model_doc["gridfs_id"])
                model_bytes = file.read()
            else:
                # Load from inline storage
                model_bytes = model_doc["model_data"]
            
            # Deserialize model state
            buffer = io.BytesIO(model_bytes)
            state_dict = torch.load(buffer, map_location='cpu')
            
            print(f"✅ Model loaded: {model_id}")
            
            return {
                "state_dict": state_dict,
                "architecture": model_doc["architecture"],
                "metadata": model_doc["metadata"]
            }
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    
    def get_user_models(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all models for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of model metadata documents (without model_data)
        """
        models = self.models.find(
            {"user_id": user_id},
            {"model_data": 0}  # Exclude large binary data
        ).sort("created_at", -1)
        
        return list(models)
    
    def set_active_model(self, user_id: str, model_id: str) -> bool:
        """
        Set active model for user (for agent gameplay)
        
        Args:
            user_id: User identifier
            model_id: Model to set as active
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": {"active_model_id": model_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error setting active model: {e}")
            return False
    
    def get_active_model_id(self, user_id: str) -> Optional[str]:
        """
        Get active model ID for user
        
        Args:
            user_id: User identifier
        
        Returns:
            Active model ID or None
        """
        user = self.get_user_by_id(user_id)
        return user.get("active_model_id") if user else None
    
    # ==================== Training Jobs ====================
    
    def create_training_job(self, user_id: str, config: Dict[str, Any]) -> str:
        """
        Create a training job record
        
        Args:
            user_id: User identifier
            config: Training configuration dict
        
        Returns:
            Training job ID
        """
        job_id = f"train_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        job_doc = {
            "job_id": job_id,
            "user_id": user_id,
            "status": "pending",
            "config": config,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "progress": 0,
            "current_epoch": 0,
            "total_epochs": config.get("epochs", 0),
            "loss_history": [],
            "error": None
        }
        
        self.training_jobs.insert_one(job_doc)
        print(f"✅ Training job created: {job_id}")
        return job_id
    
    def update_training_status(self, job_id: str, status: str, **kwargs) -> bool:
        """
        Update training job status
        
        Args:
            job_id: Training job identifier
            status: New status (pending, running, completed, failed)
            **kwargs: Additional fields to update (progress, current_epoch, error, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            update_doc = {"status": status}
            update_doc.update(kwargs)
            
            if status == "running" and "started_at" not in update_doc:
                update_doc["started_at"] = datetime.utcnow()
            elif status in ["completed", "failed"] and "completed_at" not in update_doc:
                update_doc["completed_at"] = datetime.utcnow()
            
            result = self.training_jobs.update_one(
                {"job_id": job_id},
                {"$set": update_doc}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating training status: {e}")
            return False
    
    def get_training_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get training job by ID
        
        Args:
            job_id: Training job identifier
        
        Returns:
            Training job document or None
        """
        return self.training_jobs.find_one({"job_id": job_id})
    
    def get_user_training_jobs(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get training jobs for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of jobs to return
        
        Returns:
            List of training job documents
        """
        return list(
            self.training_jobs.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
    
    # ==================== Cleanup ====================
    
    def close(self):
        """Close database connection"""
        self.client.close()
        print("✅ DatabaseManager connection closed")
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
