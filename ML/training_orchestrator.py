# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Training orchestrator for Chesster ML pipeline
# Validates data, coordinates training lifecycle, monitors progress

from typing import Dict, Optional, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import sys
import os

sys.path.append(os.path.dirname(__file__))
from chess_dataset import ChessDataset
from state_encoder import StateEncoder

# Add parent directory for data access
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.database_manager import DatabaseManager

class TrainingOrchestrator:
    """
    Orchestrates model training workflow
    
    Responsibilities:
    1. Validate training data availability and quality
    2. Prepare datasets and dataloaders
    3. Execute training loops with proper monitoring
    4. Handle checkpointing and early stopping
    5. Save trained models to database
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize orchestrator
        
        Args:
            database_manager: DatabaseManager instance for data access
        """
        self.db = database_manager
        self.encoder = StateEncoder()
        
    def validate_training_data(self, user_id: str) -> tuple:
        """
        Validate that user has sufficient data for training
        
        Args:
            user_id: User identifier
            
        Returns:
            (is_valid, message, game_count, position_count) tuple
        """
        # Get user's games
        games = self.db.get_user_games(user_id, limit=10000)
        
        if len(games) < 10:
            return False, f"Insufficient games: {len(games)} (minimum 10 required)", len(games), 0
        
        # Count total positions
        total_positions = sum(len(game.get('board_states', [])) for game in games)
        
        if total_positions < 200:
            return False, f"Insufficient positions: {total_positions} (minimum 200 required)", len(games), total_positions
        
        return True, f"Data validated: {len(games)} games, {total_positions} positions", len(games), total_positions
    
    def prepare_dataloaders(
        self,
        user_id: str,
        batch_size: int = 64,
        validation_split: float = 0.15,
        num_workers: int = 2
    ) -> tuple:
        """
        Prepare training and validation dataloaders
        
        Args:
            user_id: User identifier
            batch_size: Batch size for training
            validation_split: Fraction of data for validation
            num_workers: Number of worker processes for data loading
            
        Returns:
            (train_loader, val_loader, train_size, val_size) tuple
        """
        # Load games
        games = self.db.get_user_games(user_id, limit=10000)
        
        # Create dataset
        dataset = ChessDataset(games, encoder=self.encoder)
        
        # Split into train and validation
        val_size = int(len(dataset) * validation_split)
        train_size = len(dataset) - val_size
        
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset,
            [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )
        
        return train_loader, val_loader, train_size, val_size
    
    def train_model(
        self,
        user_id: str,
        model: nn.Module,
        architecture: str,
        epochs: int = 50,
        batch_size: int = 64,
        learning_rate: float = 0.001,
        device: str = 'cpu',
        save_checkpoints: bool = True,
        early_stopping_patience: int = 10
    ) -> Dict:
        """
        Execute full training loop
        
        Args:
            user_id: User identifier
            model: Neural network model to train
            architecture: Architecture name for saving
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimizer
            device: Device to train on (cpu, cuda, mps)
            save_checkpoints: Whether to save checkpoints during training
            early_stopping_patience: Epochs without improvement before stopping
            
        Returns:
            Training results dictionary
        """
        # Validate data
        is_valid, message, game_count, position_count = self.validate_training_data(user_id)
        if not is_valid:
            return {
                "success": False,
                "error": message,
                "games": game_count,
                "positions": position_count
            }
        
        print(f"🚀 Starting training: {architecture}")
        print(f"📊 {message}")
        
        # Prepare dataloaders
        train_loader, val_loader, train_size, val_size = self.prepare_dataloaders(
            user_id,
            batch_size=batch_size
        )
        
        print(f"📦 Train: {train_size} samples, Val: {val_size} samples")
        
        # Move model to device
        model = model.to(device)
        
        # Setup optimizer and loss
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()
        
        # Training history
        history = {
            "train_loss": [],
            "val_loss": [],
            "epochs": []
        }
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        # Training loop
        for epoch in range(1, epochs + 1):
            # Training phase
            model.train()
            train_loss = 0.0
            train_batches = 0
            
            for batch_states, batch_evals in train_loader:
                batch_states = batch_states.to(device)
                batch_evals = batch_evals.to(device)
                
                # Forward pass
                optimizer.zero_grad()
                predictions = model(batch_states)
                loss = criterion(predictions.squeeze(), batch_evals)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                train_batches += 1
            
            avg_train_loss = train_loss / train_batches
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            val_batches = 0
            
            with torch.no_grad():
                for batch_states, batch_evals in val_loader:
                    batch_states = batch_states.to(device)
                    batch_evals = batch_evals.to(device)
                    
                    predictions = model(batch_states)
                    loss = criterion(predictions.squeeze(), batch_evals)
                    
                    val_loss += loss.item()
                    val_batches += 1
            
            avg_val_loss = val_loss / val_batches
            
            # Record history
            history["train_loss"].append(avg_train_loss)
            history["val_loss"].append(avg_val_loss)
            history["epochs"].append(epoch)
            
            # Print progress
            if epoch % 5 == 0 or epoch == epochs:
                print(f"📈 Epoch {epoch}/{epochs} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")
            
            # Early stopping check
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                
                # Save best model checkpoint
                if save_checkpoints:
                    best_model_state = model.state_dict()
            else:
                patience_counter += 1
                
                if patience_counter >= early_stopping_patience:
                    print(f"⚠️  Early stopping triggered at epoch {epoch}")
                    break
        
        # Use best model if checkpoints enabled
        if save_checkpoints:
            model.load_state_dict(best_model_state)
        
        # Save final model to database
        model_name = f"{architecture}_e{epoch}"
        metadata = {
            "epochs_trained": epoch,
            "best_val_loss": best_val_loss,
            "final_train_loss": avg_train_loss,
            "training_games": game_count,
            "training_positions": position_count,
            "hyperparameters": {
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "device": device
            },
            "history": history
        }
        
        model_id = self.db.save_model(
            user_id=user_id,
            model_name=model_name,
            model_state=model.state_dict(),
            architecture=architecture,
            metadata=metadata
        )
        
        if not model_id:
            return {
                "success": False,
                "error": "Failed to save model to database"
            }
        
        # Set as active model
        self.db.set_active_model(user_id, model_id)
        
        print(f"✅ Training complete: {model_id}")
        print(f"📊 Best Val Loss: {best_val_loss:.4f}")
        
        return {
            "success": True,
            "model_id": model_id,
            "epochs_trained": epoch,
            "best_val_loss": best_val_loss,
            "final_train_loss": avg_train_loss,
            "history": history
        }
