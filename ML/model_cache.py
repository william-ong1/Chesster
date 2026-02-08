# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Model cache for chess agents
# LRU cache to avoid repeated model loading from database

from collections import OrderedDict
import torch
from typing import Optional

class ModelCache:
    """
    LRU cache for trained chess models
    """
    
    def __init__(self, capacity: int = 10):
        """
        Initialize model cache
        
        Args:
            capacity: Maximum number of models to cache
        """
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, model_id: str) -> Optional[torch.nn.Module]:
        """
        Get model from cache
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model if cached, None otherwise
        """
        if model_id in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(model_id)
            return self.cache[model_id]
        return None
    
    def put(self, model_id: str, model: torch.nn.Module):
        """
        Add model to cache
        
        Args:
            model_id: Model identifier
            model: PyTorch model
        """
        if model_id in self.cache:
            # Update existing entry
            self.cache.move_to_end(model_id)
        else:
            # Add new entry
            self.cache[model_id] = model
            
            # Evict oldest if over capacity
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    
    def clear(self):
        """Clear all cached models"""
        self.cache.clear()
