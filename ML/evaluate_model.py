# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Model evaluation utilities
# Tests trained models on validation data and generates performance metrics

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Optional
import chess
import sys
import os

sys.path.append(os.path.dirname(__file__))
from agent import Agent
from state_encoder import StateEncoder

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.database_manager import DatabaseManager

class ModelEvaluator:
    """
    Evaluates trained chess models
    
    Provides:
    1. Loss metrics (MSE, MAE) on test data
    2. Move accuracy compared to ground truth
    3. Position evaluation correlation
    4. Performance analysis and reporting
    """
    
    def __init__(self, model: nn.Module, device: str = 'cpu'):
        """
        Initialize evaluator
        
        Args:
            model: Trained neural network model
            device: Device to run evaluation on
        """
        self.model = model.to(device)
        self.device = device
        self.encoder = StateEncoder()
        
    def compute_mse(self, dataloader: DataLoader) -> float:
        """
        Compute Mean Squared Error on dataset
        
        Args:
            dataloader: DataLoader with test data
            
        Returns:
            MSE value
        """
        self.model.eval()
        criterion = nn.MSELoss()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch_states, batch_evals in dataloader:
                batch_states = batch_states.to(self.device)
                batch_evals = batch_evals.to(self.device)
                
                predictions = self.model(batch_states)
                loss = criterion(predictions.squeeze(), batch_evals)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def compute_mae(self, dataloader: DataLoader) -> float:
        """
        Compute Mean Absolute Error on dataset
        
        Args:
            dataloader: DataLoader with test data
            
        Returns:
            MAE value
        """
        self.model.eval()
        criterion = nn.L1Loss()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch_states, batch_evals in dataloader:
                batch_states = batch_states.to(self.device)
                batch_evals = batch_evals.to(self.device)
                
                predictions = self.model(batch_states)
                loss = criterion(predictions.squeeze(), batch_evals)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def evaluate_move_accuracy(
        self,
        test_games: List[Dict],
        depth: int = 2,
        max_positions: int = 100
    ) -> Dict:
        """
        Evaluate how often model picks the same moves as in test games
        
        Args:
            test_games: List of game documents with board_states
            depth: Search depth for agent
            max_positions: Maximum positions to test (for speed)
            
        Returns:
            Dictionary with accuracy metrics
        """
        agent = Agent(model=self.model, depth=depth)
        
        correct_moves = 0
        total_positions = 0
        top3_matches = 0
        
        for game in test_games:
            board_states = game.get('board_states', [])
            
            for state_idx, state in enumerate(board_states):
                if total_positions >= max_positions:
                    break
                
                # Skip last position (no next move)
                if state_idx == len(board_states) - 1:
                    continue
                
                try:
                    # Current position
                    fen = state.get('fen')
                    board = chess.Board(fen)
                    
                    # Actual move played
                    next_state = board_states[state_idx + 1]
                    actual_move_uci = next_state.get('move')
                    actual_move = chess.Move.from_uci(actual_move_uci)
                    
                    # Agent's predicted move
                    predicted_move, _ = agent.get_move(board)
                    
                    # Check if matches
                    if predicted_move == actual_move:
                        correct_moves += 1
                    
                    # Check if in top 3 legal moves (by evaluation)
                    legal_moves = list(board.legal_moves)
                    move_evals = []
                    for move in legal_moves[:10]:  # Limit to top 10 for speed
                        board.push(move)
                        eval_score = agent._evaluate_position(board)
                        board.pop()
                        move_evals.append((move, eval_score))
                    
                    # Sort by evaluation (descending for white, ascending for black)
                    move_evals.sort(key=lambda x: x[1], reverse=board.turn == chess.WHITE)
                    top3_moves = [m for m, _ in move_evals[:3]]
                    
                    if actual_move in top3_moves:
                        top3_matches += 1
                    
                    total_positions += 1
                    
                except Exception as e:
                    continue
            
            if total_positions >= max_positions:
                break
        
        accuracy = (correct_moves / total_positions * 100) if total_positions > 0 else 0.0
        top3_accuracy = (top3_matches / total_positions * 100) if total_positions > 0 else 0.0
        
        return {
            "exact_move_accuracy": accuracy,
            "top3_accuracy": top3_accuracy,
            "correct_moves": correct_moves,
            "total_positions": total_positions
        }
    
    def evaluate_correlation(self, dataloader: DataLoader) -> float:
        """
        Compute correlation between predictions and ground truth
        
        Args:
            dataloader: DataLoader with test data
            
        Returns:
            Pearson correlation coefficient
        """
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for batch_states, batch_evals in dataloader:
                batch_states = batch_states.to(self.device)
                predictions = self.model(batch_states)
                
                all_predictions.extend(predictions.squeeze().cpu().numpy())
                all_targets.extend(batch_evals.cpu().numpy())
        
        # Compute Pearson correlation
        predictions_tensor = torch.tensor(all_predictions)
        targets_tensor = torch.tensor(all_targets)
        
        pred_mean = predictions_tensor.mean()
        target_mean = targets_tensor.mean()
        
        numerator = ((predictions_tensor - pred_mean) * (targets_tensor - target_mean)).sum()
        denominator = torch.sqrt(
            ((predictions_tensor - pred_mean) ** 2).sum() * 
            ((targets_tensor - target_mean) ** 2).sum()
        )
        
        correlation = (numerator / denominator).item() if denominator != 0 else 0.0
        
        return correlation
    
    def full_evaluation(
        self,
        dataloader: DataLoader,
        test_games: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Run comprehensive evaluation suite
        
        Args:
            dataloader: DataLoader with test data
            test_games: Optional games for move accuracy testing
            
        Returns:
            Complete evaluation results
        """
        print("🧪 Starting model evaluation...")
        
        results = {
            "mse": self.compute_mse(dataloader),
            "mae": self.compute_mae(dataloader),
            "correlation": self.evaluate_correlation(dataloader)
        }
        
        print(f"📊 MSE: {results['mse']:.4f}")
        print(f"📊 MAE: {results['mae']:.4f}")
        print(f"📊 Correlation: {results['correlation']:.4f}")
        
        if test_games:
            move_accuracy = self.evaluate_move_accuracy(test_games, max_positions=50)
            results.update(move_accuracy)
            print(f"🎯 Exact Move Accuracy: {move_accuracy['exact_move_accuracy']:.2f}%")
            print(f"🎯 Top-3 Move Accuracy: {move_accuracy['top3_accuracy']:.2f}%")
        
        print("✅ Evaluation complete")
        
        return results


def evaluate_model_from_db(
    model_id: str,
    user_id: str,
    batch_size: int = 64,
    device: str = 'cpu'
) -> Dict:
    """
    Convenience function to evaluate a model from database
    
    Args:
        model_id: Model identifier in database
        user_id: User identifier for test data
        batch_size: Batch size for evaluation
        device: Device to run on
        
    Returns:
        Evaluation results dictionary
    """
    # Load model from database
    db = DatabaseManager()
    model_data = db.load_model(model_id)
    
    if not model_data:
        return {"error": "Model not found"}
    
    # Reconstruct model
    # TODO: Load architecture class dynamically based on model_data['architecture']
    # For now, assume model is already instantiated
    
    # Get test games
    games = db.get_user_games(user_id, limit=20)
    
    # Create evaluator
    # evaluator = ModelEvaluator(model, device=device)
    
    # Run evaluation
    # results = evaluator.full_evaluation(test_loader, test_games=games)
    
    return {"message": "Evaluation functionality - integrate with specific architecture"}
        
        

