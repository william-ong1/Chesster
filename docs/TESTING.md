# Chesster Testing Strategy

## Overview

This document describes our comprehensive testing strategy, including unit tests, integration tests, and how we handle edge cases across all components. Our testing framework uses **pytest** for Python backend and **Vitest + React Testing Library** for TypeScript frontend.

## Test Organization

### Feature-Specific Tests (Unit Tests)
- **Location**: On respective PR branches
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (<1s per test)
- **Coverage Goal**: >80% per component

### Integration Tests
- **Location**: `pr/integration-tests` branch
- **Purpose**: Test cross-component interactions and complete workflows
- **Speed**: Slower (1-10s per test)
- **Coverage Goal**: All critical user workflows

---

## Data Pipeline Tests (`pr/data-pipeline`)
**File**: `tests/data/test_data_pipeline.py`

### TestPGNCleaner

#### Normal Cases
- **`test_validate_valid_pgn`**: Validates properly formatted PGN with headers and moves
  - Tests standard game format with Result tag
  - Ensures no false negatives for valid games

- **`test_clean_pgn_removes_comments`**: Removes PGN comments and annotations
  - Strips `{...}` comments and `$` annotations
  - Preserves move structure

- **`test_split_multiple_games`**: Splits PGN file with multiple games
  - Handles consecutive games separated by blank lines
  - Returns correct count and individual games

#### Edge Cases
- **`test_validate_invalid_pgn`**: Detects malformed PGN
  - Missing required headers (Event, Site, Date, Round, White, Black, Result)
  - Invalid move notation
  - Truncated games
  - Returns `False` for validation

### TestPGNToBoardState

#### Normal Cases
- **`test_convert_simple_game`**: Converts basic PGN to board states
  - Parses standard opening (e4 e5 Nf3)
  - Returns list of FEN strings representing each position
  - Validates board state progression

#### Edge Cases
- **`test_invalid_pgn_returns_error`**: Handles unparseable PGN
  - Returns empty list or error for garbage input
  - Prevents crashes from malformed data

### TestDatabaseManager

#### Normal Cases
- **`test_insert_game_data`**: Stores game in MongoDB
  - Mocks MongoDB collection
  - Verifies `insert_one` called with correct data
  - Tests user_id, game_data, timestamp fields

- **`test_get_user_games`**: Retrieves user's games from database
  - Mocks MongoDB `find()` query
  - Filters by user_id
  - Returns list of game documents

#### Edge Cases
- **Connection failures**: Mocked to prevent real database dependency
- **Empty results**: Tests when user has no games
- **Large datasets**: Pagination not yet implemented (future work)

### TestPGNDownloader

#### Normal Cases
- **`test_download_chess_com_games`**: Fetches games from Chess.com API
  - Mocks `requests.get()` with sample response
  - Validates API endpoint format
  - Parses JSON response

- **`test_download_lichess_games`**: Fetches games from Lichess API
  - Mocks HTTP requests
  - Tests PGN export endpoint
  - Handles streaming responses

#### Edge Cases
- **Network errors**: Mocked `requests.exceptions.RequestException`
- **Invalid usernames**: Returns empty list or error
- **Rate limiting**: Not yet implemented (future: backoff/retry)
- **Invalid API responses**: Tests 404, 500 status codes

---

## ML Pipeline Tests (`pr/ml-pipeline`)
**File**: `tests/ML/test_ml_components.py`

### TestStateEncoder

#### Normal Cases
- **`test_encode_starting_position`**: Encodes initial chess position
  - Converts starting FEN to tensor
  - Validates shape: (8, 8, 12) for piece channels
  - Tests piece type encoding (pawn=0, knight=1, etc.)

- **`test_encode_batch`**: Encodes multiple positions
  - Batch processing for efficiency
  - Validates batch dimension

- **`test_decode_position`**: Converts tensor back to FEN
  - Round-trip encoding/decoding
  - Validates lossless conversion

#### Edge Cases
- **Invalid FEN**: Tests garbage strings, incomplete FEN
- **Special positions**: 
  - Empty squares (no pieces)
  - Promotions (pawn → queen)
  - Castling rights preservation
  - En passant square encoding

### TestModelCache

#### Normal Cases
- **`test_cache_put_and_get`**: Stores and retrieves cached evaluations
  - Tests LRU cache hit/miss
  - Validates exact value retrieval

#### Edge Cases
- **`test_cache_eviction`**: Tests LRU eviction when capacity exceeded
  - Fills cache beyond limit
  - Verifies oldest entry evicted
  - Maintains most recent entries

### TestChessDataset

#### Normal Cases
- **`test_dataset_creation`**: Creates PyTorch dataset from board states
  - Tests indexing (`__getitem__`)
  - Validates tensor shapes
  - Tests batch loading with DataLoader

#### Edge Cases
- **Empty dataset**: Tests with no games
- **Single position**: Edge case for batch size
- **Duplicate positions**: Ensures all stored (no deduplication)

### TestThreeLayerNN

#### Normal Cases
- **`test_model_forward_pass`**: Tests neural network forward pass
  - Input: (batch_size, 8, 8, 12) board state
  - Output: (batch_size, 1) evaluation score
  - Validates shape and dtype

- **`test_model_trainable`**: Verifies backpropagation works
  - Creates dummy loss
  - Calls `backward()`
  - Checks gradients computed for all parameters

#### Edge Cases
- **Single batch**: Tests batch_size=1
- **Large batch**: Tests batch_size=128 (memory constraint)
- **Invalid input shape**: Should raise error or handle gracefully

### TestAgent

#### Normal Cases
- **`test_agent_get_move`**: Generates move from valid position
  - Uses minimax/alpha-beta search
  - Returns legal move in UCI format (e.g., "e2e4")
  - Tests depth parameter

- **`test_agent_evaluate_position`**: Evaluates board state
  - Returns numeric score (positive = white advantage)
  - Tests checkmate: returns +∞ or -∞
  - Tests stalemate: returns 0.0

- **`test_alpha_beta_search`**: Tests pruning algorithm
  - Verifies correct move chosen
  - Tests depth cutoff
  - Validates alpha-beta bounds

#### Edge Cases
- **Checkmate positions**: Agent should recognize mate in 1, mate in 2
- **Stalemate**: Returns draw evaluation
- **Only one legal move**: Should return that move instantly
- **Opening position**: Tests with multiple strong moves
- **Endgame**: Tests with reduced pieces (K+Q vs K)

---

## Backend API Tests (`pr/backend-api`)
**File**: `tests/backend/test_api.py`

### TestAuthAPI

#### Normal Cases
- **`test_register_success`**: Creates new user account
  - POST `/auth/register` with username/password
  - Returns JWT token
  - Tests password hashing

- **`test_login_success`**: Authenticates existing user
  - POST `/auth/login` with credentials
  - Returns JWT token
  - Validates token structure

#### Edge Cases
- **`test_register_missing_fields`**: Returns 400 for incomplete data
- **Duplicate username**: Returns 409 Conflict
- **Weak password**: Could enforce minimum length/complexity
- **SQL injection**: Tested via mocked database (MongoDB safe by design)
- **Login with wrong password**: Returns 401 Unauthorized

### TestUploadAPI

#### Normal Cases
- **`test_upload_valid_pgn`**: Uploads PGN file
  - POST `/upload` with PGN string
  - Requires Authorization header (JWT)
  - Returns success with game count

- **`test_import_chess_com`**: Imports games from Chess.com
  - POST `/upload/chesscom` with username
  - Fetches games via API
  - Stores in database

#### Edge Cases
- **`test_upload_missing_auth`**: Returns 401 without JWT
- **Invalid PGN**: Returns 400 with error message
- **Empty PGN**: Returns 400
- **Duplicate games**: Not yet handled (future: check by date/opponent)
- **Large files**: No size limit yet (future: implement streaming)
- **Invalid Chess.com username**: Returns 404 or empty list

### TestTrainingAPI

#### Normal Cases
- **`test_start_training`**: Initiates model training
  - POST `/training/start` with config (epochs, batch_size, architecture)
  - Returns job_id for status tracking
  - Spawns background training process

- **`test_get_training_status`**: Polls training progress
  - GET `/training/status/:jobId`
  - Returns status: "pending", "running", "completed", "failed"
  - Returns metrics: loss, accuracy, epoch progress

- **`test_get_models`**: Lists available trained models
  - GET `/training/models`
  - Returns model metadata (id, name, architecture, accuracy, created_at)

#### Edge Cases
- **`test_training_insufficient_data`**: Returns 400 if user has <10 games
  - Prevents training on tiny datasets
  - Provides helpful error message

- **Invalid architecture**: Returns 400 for unknown model type
- **Concurrent training**: Not yet restricted (future: limit to 1 per user)
- **Training timeout**: Not implemented (future: kill after N hours)
- **Job_id not found**: Returns 404

### TestAgentAPI

#### Normal Cases
- **`test_get_move_valid_fen`**: Gets bot move for position
  - POST `/agent/move` with FEN and model_id
  - Returns move in UCI format and evaluation
  - Tests various positions (opening, middlegame, endgame)

- **`test_make_move_valid`**: Executes player move
  - POST `/agent/make-move` with FEN and move
  - Validates move legality
  - Returns new FEN and game status

- **`test_get_legal_moves`**: Lists all legal moves
  - POST `/agent/legal-moves` with FEN
  - Returns array of UCI moves
  - Tests move generation correctness

- **`test_get_legal_moves_for_square`**: Filters moves by source square
  - POST `/agent/legal-moves` with FEN and square (e.g., "e2")
  - Returns moves from that square only
  - Tests piece-specific move generation

#### Edge Cases - Legal Moves
- **Special Moves**:
  - **Castling**: Tests kingside (O-O) and queenside (O-O-O)
    - Verifies castling rights in FEN
    - Tests through-check prevention
    - Tests with rook/king moved previously
  - **En Passant**: Tests pawn captures in passing
    - Validates en passant square in FEN
    - Tests correct capture square
  - **Promotion**: Tests pawn reaching 8th rank
    - Returns moves like "e7e8q", "e7e8r", "e7e8b", "e7e8n"
    - Validates all 4 promotion pieces available

- **Capturing Moves**:
  - Tests piece captures (e.g., "Nxd5")
  - Tests pawn captures diagonally
  - Validates capture target is opponent piece
  - Tests captures revealing check

- **`test_make_move_illegal`**: Rejects illegal moves
  - Moving opponent's pieces
  - Moving into check
  - Moving pinned pieces illegally
  - Invalid UCI format
  - Returns 400 with error message

- **`test_get_move_invalid_fen`**: Handles malformed FEN
  - Returns 400 for garbage FEN
  - Tests missing fields in FEN

- **Check/Checkmate**:
  - Tests moves that give check
  - Tests checkmate detection (no legal moves in check)
  - Tests check evasion (must move out of check)

- **Pinned Pieces**:
  - Tests that pinned pieces can't move (or move only along pin line)
  - Example: Rook on e1, King on e2, enemy rook on e8 → King can't move to d2

- **Discovered Check**:
  - Tests moves that create discovered check
  - Validates king safety after each move

---

## Frontend Tests (`pr/frontend`)
**Files**: `tests/frontend/ChessGame.test.tsx`, `Training.test.tsx`, `ImportGames.test.tsx`, `Dashboard.test.tsx`

### ChessGame Component

#### Normal Cases
- **`test_renders_board`**: Displays 8×8 chessboard
  - Renders all 64 squares
  - Correct alternating colors
  - Shows initial piece positions

- **`test_makes_move`**: Executes valid move
  - Click source square
  - Click destination square
  - Piece moves, FEN updates
  - Turn switches

#### Edge Cases
- **`test_highlights_legal_moves`**: Shows legal moves when piece clicked
  - Highlights destination squares
  - Tests for each piece type
  - Tests special moves highlighted (castling, en passant)

- **`test_shows_check`**: Indicates when king in check
  - Highlights king square in red/yellow
  - Displays "Check!" message

- **`test_disables_on_game_over`**: Prevents moves after checkmate/stalemate
  - Board becomes non-interactive
  - Displays result ("White wins", "Black wins", "Draw")

- **`test_resets_game`**: Reset button returns to starting position
  - Clears move history
  - Resets FEN to initial
  - Re-enables moves

- **Illegal move attempt**: Click invalid square, no move made
- **Clicking empty square**: No action
- **Clicking opponent piece**: No highlights (wrong turn)

### Training Component

#### Normal Cases
- **`test_training_configuration`**: Displays training parameters
  - Epoch slider (1-100)
  - Batch size selector (16, 32, 64, 128)
  - Architecture dropdown (3_layer_nn, etc.)

- **`test_starts_training`**: Initiates training job
  - Click "Start Training" button
  - API call with config
  - Shows loading state

- **`test_displays_progress`**: Shows training metrics
  - Progress bar (% complete)
  - Current loss value
  - Current accuracy
  - Polls status every 2 seconds

#### Edge Cases
- **`test_insufficient_games_message`**: Shows warning if <10 games
  - Disables "Start Training" button
  - Displays "Upload more games to train" message

- **`test_adjust_parameters`**: Changes persist after component re-render
- **Training fails**: Displays error message from API
- **Network error**: Shows retry button

### ImportGames Component

#### Normal Cases
- **`test_renders_upload_ui`**: Displays upload options
  - File picker for PGN upload
  - Chess.com username input
  - Lichess username input

- **`test_uploads_successfully`**: Uploads PGN file
  - Select file from file picker
  - Click "Upload" button
  - Shows success message with game count

#### Edge Cases
- **`test_displays_errors`**: Shows error for invalid PGN
  - Red error message
  - Highlights problematic input

- **`test_shows_uploading_state`**: Displays loading spinner during upload
  - Disables upload button
  - Shows progress indicator

- **Large file**: Tests >1MB PGN (many games)
- **Unsupported file type**: Validates .pgn extension
- **Empty file**: Returns error
- **Chess.com user with no games**: Shows "No games found" message

### Dashboard Component

#### Normal Cases
- **`test_displays_statistics`**: Shows user stats
  - Total games uploaded
  - Total models trained
  - Win/loss/draw percentages (if available)

- **`test_displays_models`**: Lists trained models
  - Model name, architecture, accuracy
  - Created date
  - Active indicator

- **`test_activates_model`**: Sets active model for gameplay
  - Click "Activate" button
  - API call to set active model
  - Updates UI with active indicator

#### Edge Cases
- **`test_shows_active_indicator`**: Highlights currently active model
  - Green checkmark or "Active" badge
  - Only one model active at a time

- **No models yet**: Shows "Train your first model" message
- **No games yet**: Shows "Upload games to get started" message
- **Deleting model**: Not yet implemented

---

## Integration Tests (`pr/integration-tests`)
**File**: `tests/integration/test_workflows.py`

### TestEndToEndWorkflow

- **`test_upload_train_play_workflow`**: Complete user journey
  1. **Upload**: User uploads PGN via API
  2. **Store**: Games stored in MongoDB (mocked)
  3. **Retrieve**: Fetch games for training
  4. **Create Dataset**: Convert to ChessDataset
  5. **Train**: Train model for 5 epochs
  6. **Play**: Use trained model to make moves in game
  - Validates data flows correctly through all systems
  - Tests with realistic PGN (10 games)

### TestDataPipelineToMLIntegration

- **`test_pgn_to_dataset_pipeline`**: PGN string → training data
  - Parse multiple games from PGN
  - Convert each position to board state
  - Create PyTorch dataset
  - Validate dataset indexing works
  - Tests integration between `PGNCleaner`, `PGNToBoardState`, and `ChessDataset`

### TestBackendToFrontendIntegration

- **`test_agent_api_workflow`**: Frontend → Backend API calls
  - Create Flask test client
  - GET `/agent/move` with FEN (bot move)
  - POST `/agent/make-move` with player move
  - Validate responses match frontend expectations
  - Tests JWT authentication flow

### TestTrainingPipeline

- **`test_training_job_creation_and_status`**: Training lifecycle
  - POST `/training/start` with config
  - Receive job_id
  - Poll GET `/training/status/:jobId` 
  - Validate status transitions: pending → running → completed
  - Check final model saved and available via GET `/training/models`

### TestGamePlayWorkflow

- **`test_complete_game_sequence`**: Play 5 moves
  - Initialize board at starting position
  - Loop 5 times:
    - Get legal moves
    - Agent makes move
    - Update board
    - Validate board state valid
  - Tests that game state remains consistent

### TestErrorHandling

- **`test_invalid_pgn_handling`**: Graceful failure for bad PGN
  - Upload invalid PGN
  - Validate returns 400 with clear error message
  - Does not crash or corrupt database

- **`test_invalid_fen_handling`**: Graceful failure for bad FEN
  - Send malformed FEN to agent API
  - Validate returns 400 with error message
  - Does not crash agent process

---

## Test Coverage Goals

| Component | Unit Test Coverage | Integration Coverage |
|-----------|-------------------|---------------------|
| Data Pipeline | >80% | Upload → Store workflow |
| ML Pipeline | >75% | PGN → Dataset → Train |
| Backend API | >80% | All endpoints with auth |
| Frontend | >70% | User workflows |
| Agent | >75% | Move generation + evaluation |

---

## Running Tests

### All Python Tests
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Specific Component
```bash
pytest tests/data/ -v          # Data pipeline
pytest tests/ML/ -v            # ML pipeline
pytest tests/backend/ -v       # Backend API
pytest tests/integration/ -v   # Integration tests
```

### Frontend Tests
```bash
npm run test              # Run once
npm run test:ui          # Interactive UI
npm run test -- --coverage  # With coverage report
```

### Integration Tests Only
```bash
pytest -m integration tests/integration/ -v
```

---

## CI/CD Integration

Tests run automatically on:
- **Push to any PR branch**: Feature-specific tests
- **PR to main**: All tests including integration
- **Nightly**: Full test suite with coverage reports

See `.github/workflows/ci.yml` for configuration.

---

## Future Improvements

1. **Performance benchmarks**: Add timing tests for agent move generation
2. **Fuzz testing**: Random PGN/FEN inputs to find crashes
3. **Load testing**: Test backend with 100+ concurrent requests
4. **Smoke tests**: Quick sanity checks before full test run
5. **Visual regression testing**: Screenshot comparison for frontend
6. **Database fixtures**: Shared test data for consistency
7. **Test parallelization**: Run tests across multiple cores
8. **Property-based testing**: Use Hypothesis for chess rules validation
