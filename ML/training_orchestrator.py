# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Training orchestrator for Chesster ML pipeline
# Validates data, queues jobs, manages training lifecycle

from typing import Dict, Optional
import uuid

class TrainingOrchestrator:
    """
    Orchestrates model training workflow
    """
    
    def __init__(self, database_manager):
        """
        Initialize orchestrator
        
        Args:
            database_manager: DatabaseManager instance
        """
        self.db = database_manager
        self.active_jobs = {}
        
    def validate_training_data(self, user_id: str) -> tuple:
        """
        Validate that user has sufficient data for training
        
        Args:
            user_id: User identifier
            
        Returns:
            (is_valid, message) tuple
        """
        states = self.db.get_training_data(user_id)
        
        if len(states) < 500:
            return False, f"Insufficient data: {len(states)} positions (minimum 500 required)"
        
        # Count unique games
        game_ids = set()
        for state in states:
            game_metadata = state.get('game_metadata', {})
            game_id = f"{game_metadata.get('date')}_{game_metadata.get('white')}_{game_metadata.get('black')}"
            game_ids.add(game_id)
        
        if len(game_ids) < 10:
            return False, f"Insufficient games: {len(game_ids)} games (minimum 10 required)"
        
        return True, f"Data validated: {len(states)} positions from {len(game_ids)} games"
    
    def create_training_job(
        self,
        user_id: str,
        architecture: str,
        hyperparameters: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new training job
        
        Args:
            user_id: User identifier
            architecture: Model architecture name
            hyperparameters: Optional custom hyperparameters
            
        Returns:
            Job info dictionary
        """
        # Validate data
        is_valid, message = self.validate_training_data(user_id)
        if not is_valid:
            return {"success": False, "error": message}
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # TODO: Queue job for async training
        job_info = {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "user_id": user_id,
            "architecture": architecture,
            "hyperparameters": hyperparameters or {},
            "message": message
        }
        
        self.active_jobs[job_id] = job_info
        
        return job_info
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status of a training job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary or None
        """
        return self.active_jobs.get(job_id)
