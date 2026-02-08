# ML Pipeline Component

## Code Owners
**Primary Team:** @RaghavRamesh125 @William-Ong1 @danyuanwang @lbmlkCodes @shreyanmitra

See root [CODEOWNERS](../CODEOWNERS) for review assignments.

## Components
- `main.py` - ML pipeline orchestration
- `training.py` - Model training logic
- `agent.py` - Chess agent with alpha-beta search
- `evaluate_model.py` - Model evaluation (MSE)
- `state_encoder.py` - FEN to tensor conversion
- `chess_dataset.py` - PyTorch Dataset
- `training_orchestrator.py` - Job management
- `model_cache.py` - LRU model cache
- `model_architectures/` - Neural network architectures
  - `3_layer_nn.py` - 3-layer baseline model

## Architecture
- **Evaluation Network**: Models output position scores (not direct moves)
- **Search**: Alpha-beta pruning to select moves from evaluations
- **Training**: Weighted sum of player moves + Stockfish evaluations
- **State Encoding**: 14×8×8 tensors (12 piece channels + 2 metadata)

## Training Workflow
1. Retrieve training data from MongoDB
2. Encode FEN states to tensors
3. Train evaluation network
4. Save model to MongoDB (GridFS for >16MB)
5. Cache model for inference

## Status
🚧 Scaffolded - implementation in progress

## Next Steps for ML Team
1. Complete `training.py` using `StateEncoder` and `ChessDataset`
2. Implement alpha-beta search in `agent.py`
3. Integrate Stockfish for training guidance
4. Finish `evaluate_model.py` MSE calculation
5. Add more architectures to `model_architectures/`
6. Write unit tests in `tests/ML/`
