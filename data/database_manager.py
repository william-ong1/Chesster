# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# MongoDB database manager for Chesster
# Handles connections and CRUD operations for game_data, models, and users collections

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import List, Dict, Optional
import os
from datetime import datetime

class DatabaseManager:
    """
    Manages MongoDB connections and operations for Chesster
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: MongoDB connection string (defaults to env var)
        """
        self.connection_string = connection_string or os.getenv(
            'MONGODB_URI',
            'mongodb://localhost:27017/'
        )
        self.client = None
        self.db = None
        self._connect()
        
    def _connect(self):
        """Establish MongoDB connection and create indexes"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client['chesster']
            
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for collections"""
        # game_data collection indexes
        self.db.game_data.create_index([("user_id", ASCENDING)])
        self.db.game_data.create_index([("user_id", ASCENDING), ("game_id", ASCENDING)])
        
        # models collection indexes
        self.db.models.create_index([("user_id", ASCENDING)])
        self.db.models.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])
        
        # users collection indexes
        self.db.users.create_index([("user_id", ASCENDING)], unique=True)
        self.db.users.create_index([("username", ASCENDING)], unique=True)
        self.db.users.create_index([("email", ASCENDING)], unique=True)
    
    # === Game Data Operations ===
    
    def insert_game_data(self, user_id: str, games: List[Dict]) -> bool:
        """
        Insert game data for a user
        
        Args:
            user_id: User identifier
            games: List of game dictionaries with states
            
        Returns:
            True if successful
        """
        try:
            document = {
                "user_id": user_id,
                "games": games,
                "uploaded_at": datetime.utcnow()
            }
            self.db.game_data.insert_one(document)
            return True
        except Exception as e:
            print(f"Error inserting game data: {e}")
            return False
    
    def get_user_games(self, user_id: str) -> List[Dict]:
        """
        Retrieve all games for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of game documents
        """
        return list(self.db.game_data.find({"user_id": user_id}))
    
    def get_training_data(self, user_id: str) -> List[Dict]:
        """
        Get all board states for training
        
        Args:
            user_id: User identifier
            
        Returns:
            List of {fen, move_made, move_number} dictionaries
        """
        games = self.get_user_games(user_id)
        all_states = []
        for game_doc in games:
            for game in game_doc.get("games", []):
                all_states.extend(game.get("states", []))
        return all_states
    
    # === Model Operations ===
    
    def save_model(
        self,
        user_id: str,
        model_id: str,
        model_data: bytes,
        metadata: Dict
    ) -> bool:
        """
        Save trained model to database
        
        Args:
            user_id: User identifier
            model_id: Unique model identifier
            model_data: Serialized model bytes
            metadata: Model metadata (architecture, hyperparameters, etc.)
            
        Returns:
            True if successful
        """
        try:
            # For models > 16MB, use GridFS (TODO)
            # For now, store directly in models collection
            
            document = {
                "user_id": user_id,
                "model_id": model_id,
                "model_data": model_data,
                "metadata": metadata,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            # Deactivate previous active models
            self.db.models.update_many(
                {"user_id": user_id, "is_active": True},
                {"$set": {"is_active": False}}
            )
            
            # Insert new model
            self.db.models.insert_one(document)
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def get_active_model(self, user_id: str) -> Optional[Dict]:
        """
        Get the active model for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Model document or None
        """
        return self.db.models.find_one({
            "user_id": user_id,
            "is_active": True
        })
    
    # === User Operations ===
    
    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        password_hash: str
    ) -> bool:
        """
        Create a new user account
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: Email address
            password_hash: Hashed password
            
        Returns:
            True if successful, False if user exists
        """
        try:
            document = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
            self.db.users.insert_one(document)
            return True
            
        except DuplicateKeyError:
            return False
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.db.users.find_one({"username": username})
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
