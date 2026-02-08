# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Model cache for chess agents
# LRU cache to avoid repeated model loading from database

from collections import OrderedDict
import torch
import io
from typing import Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.database_manager import DatabaseManager
from ML.model_architectures.three_layer_nn import ThreeLayerNN

class ModelCache:
    """
    LRU cache for trained chess models
    
    Automatically loads models from MongoDB when requested.
    Uses LRU eviction policy to manage memory.
    """
    
    def __init__(self, capacity: int = 10, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize model cache
        
        Args:
            capacity: Maximum number of models to cache
            db_manager: DatabaseManager instance (creates new if None)
        """
        self.capacity = capacity
        self.cache: OrderedDict[str, torch.nn.Module] = OrderedDict()
        self.db_manager = db_manager or DatabaseManager()
        self._own_db = db_manager is None  # Track if we created the DB manager
        
    def get(self, model_id: str) -> Optional[torch.nn.Module]:
        """
        Get model from cache or load from database
        
        Args:
            model_id: Model identifier
            
        Returns:
            Loaded PyTorch model or None if not found
        """
        # Check cache first
        if model_id in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(model_id)
            print(f"✅ Model {model_id} loaded from cache")
            return self.cache[model_id]
        
        # Load from database
        model = self._load_from_database(model_id)
        
        if model is not None:
            # Add to cache
            self.put(model_id, model)
            print(f"✅ Model {model_id} loaded from database and cached")
        
        return model
    
    def _load_from_database(self, model_id: str) -> Optional[torch.nn.Module]:
        """
        Load model from MongoDB
        
        Args:
            model_id: Model identifier
            
        Returns:
            PyTorch model or None
        """
        try:
            # Get model metadata
            model_doc = self.db_manager.get_model_metadata(model_id)
            
            if not model_doc:
                print(f"❌ Model {model_id} not found in database")
                return None
            
            # Load model bytes
            model_bytes = self.db_manager.load_model(model_id)
            
            if not model_bytes:
                print(f"❌ Failed to load model data for {model_id}")
                return None
            
            # Get architecture from metadata
            architecture = model_doc.get('metadata', {}).get('architecture', '3_layer_nn')
            
            # Instantiate model architecture
            if architecture == '3_layer_nn':
                model = ThreeLayerNN()
            else:
                print(f"❌ Unknown architecture: {architecture}")
                return None
            
            # Load state dict from bytes
            buffer = io.BytesIO(model_bytes)
            state_dict = torch.load(buffer, map_location='cpu')
            model.load_state_dict(state_dict)
            model.eval()  # Set to evaluation mode
            
            return model
            
        except Exception as e:
            print(f"❌ Error loading model {model_id}: {e}")
            return None
    
    def put(self, model_id: str, model: torch.nn.Module):
        """
        Add model to cache
        
        Args:
            model_id: Model identifier
            model: PyTorch model
        """
        if model_id in self.cache:
            # Update existing entry and move to end
            self.cache.move_to_end(model_id)
            self.cache[model_id] = model
        else:
            # Add new entry
            self.cache[model_id] = model
            
            # Evict oldest if over capacity
            if len(self.cache) > self.capacity:
                evicted_id, _ = self.cache.popitem(last=False)
                print(f"🗑️ Evicted model {evicted_id} from cache (LRU)")
    
    def contains(self, model_id: str) -> bool:
        """
        Check if model is in cache
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if in cache
        """
        return model_id in self.cache
    
    def size(self) -> int:
        """
        Get number of cached models
        
        Returns:
            Cache size
        """
        return len(self.cache)
    
    def get_cached_ids(self) -> list:
        """
        Get list of cached model IDs
        
        Returns:
            List of model IDs (most recent first)
        """
        return list(reversed(self.cache.keys()))
    
    def clear(self):
        """Clear all cached models"""
        count = len(self.cache)
        self.cache.clear()
        print(f"🗑️ Cleared {count} models from cache")
    
    def remove(self, model_id: str) -> bool:
        """
        Remove specific model from cache
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if removed, False if not in cache
        """
        if model_id in self.cache:
            del self.cache[model_id]
            print(f"🗑️ Removed model {model_id} from cache")
            return True
        return False
    
    def preload(self, model_ids: list):
        """
        Preload multiple models into cache
        
        Args:
            model_ids: List of model identifiers to preload
        """
        for model_id in model_ids:
            if not self.contains(model_id):
                self.get(model_id)  # This will load and cache
    
    def close(self):
        """Close database connection if we own it"""
        if self._own_db and self.db_manager:
            self.db_manager.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

