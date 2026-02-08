# Chesster AI Agent Instructions

## Project Overview
Chesster is a chess playstyle replication bot that learns from a user's historical chess games (PGN format) to mimic their playing style. The system consists of three main pipelines: Data Processing, ML Training/Inference, and Frontend (planned).

## Architecture & Data Flow

**Data Pipeline** (`data/`):
1. `PGN_cleaner.py` - Sanitizes raw PGN game data
2. `PGN_to_board_state.py` - Converts PGN strings to FEN board states (e.g., `"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"`)

**ML Pipeline** (`ML/`):
1. `main.py` - Orchestrates data retrieval from MongoDB, training/testing workflow
2. `training.py` - Supervised learning using weighted sum of player data + chess engine evaluation
3. `agent.py` - Wraps trained models for gameplay with alpha-beta pruning search
4. `evaluate_model.py` - Tests model accuracy against player moves using MSE
5. `model_architectures/` - PyTorch model definitions (e.g., `3_layer_nn.py`)

**Data Storage**: MongoDB stores raw games, trained models (by model_id), and evaluation metrics

## Key Technologies & Dependencies
- **PyTorch** (`>=2.0.0`) - Neural network training and inference
- **python-chess** (`>=1.999`) - Chess logic, board representation, move validation
- **pymongo** (`>=4.0.0`) - MongoDB integration for data/model persistence
- **Stockfish** - Chess engine being fine-tuned for playstyle replication (replacing original Sunfish NNUE approach)

## Critical Patterns & Conventions

### Board Representation
- Use FEN (Forsyth-Edwards Notation) strings for board states
- Use `chess.Board()` from python-chess for move generation and validation
- Board states are the input features; moves are the labels
- State encoding: Convert FEN to 12×8×8 tensors (12 piece-type channels) + castling/en passant/turn metadata

### Model Workflow
1. Models are stored in MongoDB with unique `model_id`
2. Models saved to GridFS for files >16MB (models collection for metadata, GridFS for binary data)
3. Agent initialization: `Agent(model_id)` loads model via `torch.load(model)`
4. Training uses `DataLoader` for batching player data
5. Models are **evaluation networks** (not policy networks) - output position scores, then use minimax/alpha-beta search to select moves
6. Training uses weighted sum of player's move frequencies + Stockfish evaluations

### MongoDB Schema Conventions
- `game_data` collection: `{user_id, games[{game_id, metadata, states[{fen, move_made, move_number}]}]}`
- `models` collection: `{user_id, model_id, model_file_id (GridFS ref), metadata, is_active}`
- `users` collection: `{user_id, username, email, password_hash, created_at, last_login}`
- Indexes: compound index on `(user_id, game_id)` for game_data, `(user_id, is_active)` for models

### Type Hints
All functions use Python type hints (e.g., `def get_move(self, board: chess.Board) -> chess.Move:`)

## Development Workflows

### Training a Model
```python
# Typical flow (from ML/training.py pattern):
architecture = "3_layer_nn"  # or other from model_architectures/
dataloader = # DataLoader with processed board states
trainer = Training(architecture, dataloader)
trainer.train()
# Model saved to MongoDB after training
```

### Running Inference
```python
# From ML/agent.py pattern:
agent = Agent(model_id="<mongo_model_id>")
move = agent.get_move(board)  # Returns chess.Move object
agent.make_move(move)
```

### Processing Chess Data
- Input: PGN strings from chess platforms (Chess.com, Lichess)
- Clean with `PGN_cleaner.py` → Convert with `PGN_to_board_state.py`
- Output: List of FEN strings for each game position

## Team Structure & Code Ownership
- **ML Team**: 5 members (Raghav, William, Danyuan, Lebam, Shreyan) - `/ML/`
- **Data Team**: 3 members (Danyuan, Lebam, Mason) - `/data/`
- **Frontend Team**: 2 members (Shreyan, Lebam) - `/frontend/`

See [CODEOWNERS](../CODEOWNERS) for review assignments.

## Current State & TODOs
⚠️ **This is an early-stage project** - most files contain skeleton code with `#TODO` markers. When implementing:
- Follow existing class structures and method signatures
- Maintain MongoDB integration patterns for data/model persistence
- Preserve type hints and chess.Board/chess.Move interfaces
- Reference `3_layer_nn.py` for model architecture patterns

## Integration Notes
- **Frontend-Backend Communication**: Team exploring TypeScript (UI) ↔ Python (ML/Data) integration (see StatusReports)
- **Planned Features**: Agent uses known positions (direct lookup) vs unknown positions (model inference)
