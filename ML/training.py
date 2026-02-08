# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Code for training the model from a given architecture, using supervised learning and a weighted sum of the player's data
# and the evaluation of a preexisting chess engine (Stockfish).
# Pull data from MongoDB and use it to train the model.
# After training, save the model to MongoDB.

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import sys
import os
from typing import Dict, Optional, Tuple
from datetime import datetime
import uuid

# Import model architectures
sys.path.append(os.path.dirname(__file__))
from model_architectures.3_layer_nn import ThreeLayerNN


class Training:
    """
    Handles training of chess evaluation networks.
    
    Trains models to output position evaluations (not direct moves) using:
    1. Player move frequencies from historical games
    2. Stockfish evaluations for position scoring (optional weighting)
    
    The trained model is an evaluation network that scores positions,
    which are then used by the agent with alpha-beta search to select moves.
    """
    
    def __init__(
        self, 
        architecture: str, 
        dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        learning_rate: float = 0.001,
        device: str = 'cpu'
    ):
        """
        Initialize training configuration.
        
        Args:
            architecture: Name of model architecture from model_architectures folder
                         Currently supports: "3_layer_nn"
            dataloader: PyTorch DataLoader with training data
            val_dataloader: Optional validation DataLoader for tracking generalization
            learning_rate: Learning rate for Adam optimizer (default: 0.001)
            device: 'cpu' or 'cuda' for GPU training
        """
        self.architecture = architecture
        self.dataloader = dataloader
        self.val_dataloader = val_dataloader
        self.learning_rate = learning_rate
        self.device = torch.device(device)
        
        # Initialize model based on architecture name
        self.model = self._load_architecture(architecture)
        self.model = self.model.to(self.device)
        
        # Setup optimizer - Adam is standard for deep learning
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Loss function: MSE for evaluation network (regression task)
        # We're predicting position scores, not classification
        self.criterion = nn.MSELoss()
        
        # Training metrics tracking
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'epochs_completed': 0
        }
        
        # Generate unique model ID for saving to MongoDB
        self.model_id = str(uuid.uuid4())
        
    def _load_architecture(self, architecture: str) -> nn.Module:
        """
        Load model architecture by name.
        
        Args:
            architecture: Architecture name (e.g., "3_layer_nn")
            
        Returns:
            PyTorch model instance
            
        Raises:
            ValueError: If architecture name not recognized
        """
        # Model expects input: 14 channels × 8 × 8 board
        # (12 piece channels + 2 metadata channels as per state_encoder.py)
        input_size = 14 * 8 * 8  # Flattened board tensor
        
        # Output: Single evaluation score for the position
        # Positive = good for white, negative = good for black
        output_size = 1
        
        if architecture == "3_layer_nn":
            # Simple 3-layer feedforward network (baseline model)
            hidden_size = 256  # Hidden layer neurons
            return ThreeLayerNN(input_size, hidden_size, output_size)
        else:
            raise ValueError(f"Unknown architecture: {architecture}. "
                           f"Available: '3_layer_nn'")
    
    def train(
        self, 
        epochs: int = 50,
        save_every: int = 10,
        verbose: bool = True
    ) -> Dict:
        """
        Main training loop - trains model for specified number of epochs.
        
        This implements supervised learning where the model learns to evaluate
        chess positions based on historical player moves and optional engine evaluations.
        
        Args:
            epochs: Number of training epochs (full passes through dataset)
            save_every: Save checkpoint every N epochs
            verbose: Print progress during training
            
        Returns:
            Dictionary with training metrics and model_id
            
        Example:
            >>> trainer = Training("3_layer_nn", train_loader)
            >>> results = trainer.train(epochs=50)
            >>> print(f"Final loss: {results['final_train_loss']}")
        """
        if verbose:
            print(f"Starting training: {self.architecture}")
            print(f"Device: {self.device}")
            print(f"Epochs: {epochs}")
            print(f"Learning rate: {self.learning_rate}")
            print("-" * 50)
        
        for epoch in range(epochs):
            # Training phase
            train_loss = self._train_epoch()
            self.training_history['train_loss'].append(train_loss)
            
            # Validation phase (if validation data provided)
            if self.val_dataloader is not None:
                val_loss = self._validate_epoch()
                self.training_history['val_loss'].append(val_loss)
            else:
                val_loss = None
            
            self.training_history['epochs_completed'] += 1
            
            # Print progress
            if verbose:
                if val_loss is not None:
                    print(f"Epoch {epoch+1}/{epochs} - "
                          f"Train Loss: {train_loss:.4f} - "
                          f"Val Loss: {val_loss:.4f}")
                else:
                    print(f"Epoch {epoch+1}/{epochs} - "
                          f"Train Loss: {train_loss:.4f}")
            
            # Save checkpoint periodically
            if (epoch + 1) % save_every == 0:
                checkpoint_path = f"checkpoint_epoch_{epoch+1}.pth"
                self._save_checkpoint(checkpoint_path)
                if verbose:
                    print(f"  → Checkpoint saved: {checkpoint_path}")
        
        if verbose:
            print("-" * 50)
            print(f"Training complete! Model ID: {self.model_id}")
        
        # Return training results
        return {
            'model_id': self.model_id,
            'architecture': self.architecture,
            'epochs': epochs,
            'final_train_loss': self.training_history['train_loss'][-1],
            'final_val_loss': self.training_history['val_loss'][-1] if self.val_dataloader else None,
            'training_history': self.training_history
        }
    
    def _train_epoch(self) -> float:
        """
        Train for one epoch (one pass through training data).
        
        Returns:
            Average loss for this epoch
        """
        self.model.train()  # Set model to training mode
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (board_tensors, targets) in enumerate(self.dataloader):
            # Move data to device (CPU or GPU)
            board_tensors = board_tensors.to(self.device)
            targets = targets.to(self.device).float()
            
            # Flatten board tensor: (batch, 14, 8, 8) → (batch, 896)
            batch_size = board_tensors.size(0)
            board_flat = board_tensors.view(batch_size, -1)
            
            # Zero gradients from previous iteration
            self.optimizer.zero_grad()
            
            # Forward pass: predict position evaluation
            predictions = self.model(board_flat)
            
            # Calculate loss: MSE between prediction and target evaluation
            # Target could be: player win rate, Stockfish eval, or combination
            loss = self.criterion(predictions.squeeze(), targets)
            
            # Backward pass: compute gradients
            loss.backward()
            
            # Update model weights
            self.optimizer.step()
            
            # Track loss
            total_loss += loss.item()
            num_batches += 1
        
        # Return average loss across all batches
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def _validate_epoch(self) -> float:
        """
        Validate model on validation set (no gradient updates).
        
        Returns:
            Average validation loss
        """
        self.model.eval()  # Set model to evaluation mode
        total_loss = 0.0
        num_batches = 0
        
        # Don't compute gradients during validation (saves memory)
        with torch.no_grad():
            for board_tensors, targets in self.val_dataloader:
                # Move data to device
                board_tensors = board_tensors.to(self.device)
                targets = targets.to(self.device).float()
                
                # Flatten board tensor
                batch_size = board_tensors.size(0)
                board_flat = board_tensors.view(batch_size, -1)
                
                # Forward pass only
                predictions = self.model(board_flat)
                loss = self.criterion(predictions.squeeze(), targets)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def _save_checkpoint(self, filepath: str):
        """
        Save training checkpoint to local file.
        
        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'model_id': self.model_id,
            'architecture': self.architecture
        }
        torch.save(checkpoint, filepath)
    
    def save_model_to_db(self, database_manager, user_id: str, metadata: Optional[Dict] = None):
        """
        Save trained model to MongoDB for deployment.
        
        This should be called after training completes to persist the model
        for use by the chess agent during gameplay.
        
        Args:
            database_manager: DatabaseManager instance for MongoDB operations
            user_id: User this model belongs to
            metadata: Optional additional metadata (hyperparameters, accuracy, etc.)
            
        Returns:
            True if save successful, False otherwise
        """
        # Serialize model to bytes
        import io
        buffer = io.BytesIO()
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'architecture': self.architecture,
            'model_id': self.model_id,
            'trained_at': datetime.utcnow().isoformat()
        }, buffer)
        model_bytes = buffer.getvalue()
        
        # Prepare metadata
        full_metadata = {
            'architecture': self.architecture,
            'epochs': self.training_history['epochs_completed'],
            'final_train_loss': self.training_history['train_loss'][-1] if self.training_history['train_loss'] else None,
            'final_val_loss': self.training_history['val_loss'][-1] if self.training_history['val_loss'] else None,
            'training_date': datetime.utcnow().isoformat(),
            'hyperparameters': {
                'learning_rate': self.learning_rate,
                'optimizer': 'Adam',
                'loss_function': 'MSE'
            }
        }
        
        # Add user-provided metadata
        if metadata:
            full_metadata.update(metadata)
        
        # Save to MongoDB
        success = database_manager.save_model(
            user_id=user_id,
            model_id=self.model_id,
            model_data=model_bytes,
            metadata=full_metadata
        )
        
        return success
    
    def get_training_metrics(self) -> Dict:
        """
        Get current training metrics and history.
        
        Returns:
            Dictionary with loss history and training stats
        """
        return {
            'model_id': self.model_id,
            'architecture': self.architecture,
            'epochs_completed': self.training_history['epochs_completed'],
            'train_loss_history': self.training_history['train_loss'],
            'val_loss_history': self.training_history['val_loss'],
            'current_train_loss': self.training_history['train_loss'][-1] if self.training_history['train_loss'] else None,
            'current_val_loss': self.training_history['val_loss'][-1] if self.training_history['val_loss'] else None
        }




    