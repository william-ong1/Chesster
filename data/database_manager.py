# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# MongoDB database manager for Chesster
# Handles connections and CRUD operations for game_data, models, and users collections

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import gridfs
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
import io

class DatabaseManager:
    """
    Manages MongoDB connections and operations for Chesster
    
    Handles:
    - Game data storage (board states, moves)
    - Model storage (using GridFS for files >16MB)
    - User account management
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: MongoDB connection string (defaults to env var)
        """
        self.connection_string = connection_string or os.getenv(
            'MONGO_URI',
            'mongodb://localhost:27017/'
        )
        self.client: Optional[MongoClient] = None
        self.db = None
        self.fs: Optional[gridfs.GridFS] = None
        self._connect()
        
    def _connect(self):
        """Establish MongoDB connection and create indexes"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client['chesster']
            self.fs = gridfs.GridFS(self.db)
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for collections"""
        # game_data collection indexes
        self.db.game_data.create_index([("user_id", ASCENDING)])
        self.db.game_data.create_index([("user_id", ASCENDING), ("uploaded_at", ASCENDING)])
        
        # models collection indexes
        self.db.models.create_index([("user_id", ASCENDING)])
        self.db.models.create_index([("model_id", ASCENDING)], unique=True)
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
            games: List of game dictionaries with format:
                   [{game_id, metadata, states: [{fen, move_made, move_number}]}]
            
        Returns:
            True if successful
        """
        try:
            document = {
                "user_id": user_id,
                "games": games,
                "uploaded_at": datetime.utcnow()
            }
            result = self.db.game_data.insert_one(document)
            print(f"✅ Inserted game data for user {user_id}: {len(games)} games")
            return result.acknowledged
        except Exception as e:
            print(f"❌ Error inserting game data: {e}")
            return False
    
    def get_user_games(self, user_id: str) -> List[Dict]:
        """
        Retrieve all games for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of game documents
        """
        try:
            games = list(self.db.game_data.find({"user_id": user_id}))
            return games
        except Exception as e:
            print(f"❌ Error fetching user games: {e}")
            return []
    
    def get_training_data(self, user_id: str) -> List[Dict]:
        """
        Get all board states for training
        
        Args:
            user_id: User identifier
            
        Returns:
            List of {fen, move_made, move_number, game_id} dictionaries
        """
        games = self.get_user_games(user_id)
        all_states = []
        for game_doc in games:
            for game in game_doc.get("games", []):
                game_id = game.get("game_id")
                for state in game.get("states", []):
                    state["game_id"] = game_id  # Add game_id to each state
                    all_states.append(state)
        return all_states
    
    def get_game_count(self, user_id: str) -> int:
        """
        Get total number of games for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Total game count
        """
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$games"},
                {"$count": "total"}
            ]
            result = list(self.db.game_data.aggregate(pipeline))
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"❌ Error counting games: {e}")
            return 0
    
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
        
        Uses GridFS for models >16MB, direct storage for smaller models
        
        Args:
            user_id: User identifier
            model_id: Unique model identifier
            model_data: Serialized model bytes
            metadata: Model metadata (architecture, hyperparameters, metrics, etc.)
            
        Returns:
            True if successful
        """
        try:
            # Check if model should use GridFS (>16MB)
            use_gridfs = len(model_data) > 16 * 1024 * 1024
            
            if use_gridfs:
                # Store in GridFS
                file_id = self.fs.put(
                    model_data,
                    filename=f"model_{model_id}",
                    user_id=user_id,
                    model_id=model_id
                )
                
                document = {
                    "user_id": user_id,
                    "model_id": model_id,
                    "model_file_id": file_id,
                    "storage_type": "gridfs",
                    "metadata": metadata,
                    "is_active": False,  # Set to active later
                    "created_at": datetime.utcnow()
                }
            else:
                # Store directly in collection
                document = {
                    "user_id": user_id,
                    "model_id": model_id,
                    "model_data": model_data,
                    "storage_type": "direct",
                    "metadata": metadata,
                    "is_active": False,
                    "created_at": datetime.utcnow()
                }
            
            # Insert model document
            self.db.models.insert_one(document)
            print(f"✅ Saved model {model_id} for user {user_id} (storage: {document['storage_type']})")
            return True
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def load_model(self, model_id: str) -> Optional[bytes]:
        """
        Load model data from database
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model bytes or None if not found
        """
        try:
            model_doc = self.db.models.find_one({"model_id": model_id})
            
            if not model_doc:
                print(f"❌ Model {model_id} not found")
                return None
            
            if model_doc["storage_type"] == "gridfs":
                # Load from GridFS
                file_id = model_doc["model_file_id"]
                grid_out = self.fs.get(file_id)
                return grid_out.read()
            else:
                # Load from document
                return model_doc["model_data"]
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict]:
        """
        Get model metadata without loading the full model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Metadata dictionary or None
        """
        try:
            model_doc = self.db.models.find_one(
                {"model_id": model_id},
                {"metadata": 1, "is_active": 1, "created_at": 1}
            )
            return model_doc if model_doc else None
        except Exception as e:
            print(f"❌ Error fetching model metadata: {e}")
            return None
    
    def get_active_model(self, user_id: str) -> Optional[Dict]:
        """
        Get the active model for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Model document (without model_data) or None
        """
        try:
            return self.db.models.find_one(
                {"user_id": user_id, "is_active": True},
                {"model_data": 0}  # Exclude large model data
            )
        except Exception as e:
            print(f"❌ Error fetching active model: {e}")
            return None
    
    def set_active_model(self, user_id: str, model_id: str) -> bool:
        """
        Set a model as active for a user
        
        Args:
            user_id: User identifier
            model_id: Model identifier to activate
            
        Returns:
            True if successful
        """
        try:
            # Deactivate all models for this user
            self.db.models.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            # Activate the specified model
            result = self.db.models.update_one(
                {"user_id": user_id, "model_id": model_id},
                {"$set": {"is_active": True}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Set model {model_id} as active for user {user_id}")
                return True
            else:
                print(f"⚠️ Model {model_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting active model: {e}")
            return False
    
    def get_user_models(self, user_id: str) -> List[Dict]:
        """
        Get all models for a user (metadata only, no model data)
        
        Args:
            user_id: User identifier
            
        Returns:
            List of model documents
        """
        try:
            return list(self.db.models.find(
                {"user_id": user_id},
                {"model_data": 0}  # Exclude large model data
            ).sort("created_at", -1))
        except Exception as e:
            print(f"❌ Error fetching user models: {e}")
            return []
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from database
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if successful
        """
        try:
            model_doc = self.db.models.find_one({"model_id": model_id})
            
            if not model_doc:
                return False
            
            # Delete from GridFS if applicable
            if model_doc.get("storage_type") == "gridfs":
                file_id = model_doc["model_file_id"]
                self.fs.delete(file_id)
            
            # Delete model document
            self.db.models.delete_one({"model_id": model_id})
            print(f"✅ Deleted model {model_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting model: {e}")
            return False
    
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
            print(f"✅ Created user: {username}")
            return True
            
        except DuplicateKeyError:
            print(f"⚠️ User already exists: {username}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            return self.db.users.find_one({"email": email})
        except Exception as e:
            print(f"❌ Error fetching user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            return self.db.users.find_one({"username": username})
        except Exception as e:
            print(f"❌ Error fetching user by username: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        try:
            return self.db.users.find_one({"user_id": user_id})
        except Exception as e:
            print(f"❌ Error fetching user by ID: {e}")
            return None
    
    def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            result = self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating last login: {e}")
            return False
    
    # === Statistics Operations ===
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with game count, total positions, etc.
        """
        try:
            game_count = self.get_game_count(user_id)
            
            # Count total positions
            training_data = self.get_training_data(user_id)
            position_count = len(training_data)
            
            # Count models
            models = self.get_user_models(user_id)
            model_count = len(models)
            
            return {
                "game_count": game_count,
                "position_count": position_count,
                "model_count": model_count,
                "has_active_model": any(m.get("is_active") for m in models)
            }
        except Exception as e:
            print(f"❌ Error fetching user stats: {e}")
            return {
                "game_count": 0,
                "position_count": 0,
                "model_count": 0,
                "has_active_model": False
            }
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
