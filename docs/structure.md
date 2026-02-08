# Project Structure

```
Chesster/
├── .github/
│   ├── copilot-instructions.md    # AI agent guidance
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI/CD
│
├── backend/                        # Flask/FastAPI backend
│   ├── __init__.py
│   ├── app.py                      # Main Flask application
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── upload.py               # PGN upload endpoints
│   │   ├── training.py             # Training endpoints
│   │   └── agent.py                # Gameplay endpoints
│   └── auth/                       # Authentication
│       ├── __init__.py
│       └── authentication.py       # JWT auth logic
│
├── data/                           # Data pipeline
│   ├── __init__.py
│   ├── PGN_cleaner.py              # Sanitize PGN data
│   ├── PGN_to_board_state.py      # Convert PGN to FEN
│   ├── pgn_downloader.py           # Download from Chess.com/Lichess
│   ├── pgn_parser.py               # Parse PGN to structured data
│   ├── game_validator.py           # Filter low-quality games
│   ├── move_extractor.py           # Extract board states and moves
│   ├── database_manager.py         # MongoDB operations
│   └── utils/
│       └── __init__.py
│
├── ML/                             # Machine learning pipeline
│   ├── __init__.py
│   ├── main.py                     # ML pipeline orchestration
│   ├── training.py                 # Model training logic
│   ├── agent.py                    # Chess agent with search
│   ├── evaluate_model.py           # Model evaluation
│   ├── state_encoder.py            # FEN to tensor conversion
│   ├── chess_dataset.py            # PyTorch Dataset
│   ├── training_orchestrator.py   # Job management
│   ├── model_cache.py              # LRU model cache
│   ├── model_architectures/
│   │   └── 3_layer_nn.py           # 3-layer neural network
│   └── utils/
│       └── __init__.py
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── data/
│   │   └── test_data_pipeline.py
│   ├── ML/
│   │   └── test_ml_components.py
│   └── backend/
│       └── test_api.py
│
├── config/                         # Configuration
│   ├── __init__.py
│   ├── config.py                   # Flask config classes
│   └── .env.example                # Environment template
│
├── models/                         # Saved trained models
│   └── .gitkeep
│
├── docs/                           # Documentation
│   ├── README.md
│   ├── setup.md
│   ├── api.md
│   └── (more docs to be added)
│
├── StatusReports/                  # Weekly status reports
│   ├── [TEMPLATE]chesster-YYYYMMDD.md
│   ├── chesster-20260128.md
│   └── chesster-20260204.md
│
├── .gitignore                      # Git ignore rules
├── CODEOWNERS                      # Code review assignments
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
└── Chesster_Planning_Document.md  # Detailed planning doc
```

## Component Responsibilities

### Backend (`backend/`)
Flask/FastAPI application exposing REST API for:
- User authentication (JWT)
- PGN data upload
- Model training requests
- Chess move generation

### Data Pipeline (`data/`)
Processes chess game data:
1. Download games from platforms
2. Parse and validate PGN
3. Extract board states (FEN) and moves
4. Store in MongoDB

### ML Pipeline (`ML/`)
Trains and deploys chess bots:
1. Load training data from MongoDB
2. Train evaluation networks (PyTorch)
3. Implement alpha-beta search for move selection
4. Cache models for fast inference

### Tests (`tests/`)
Comprehensive test coverage:
- Unit tests for components
- Integration tests for API
- Fixtures in conftest.py

### Config (`config/`)
Environment and application configuration:
- Development, Testing, Production configs
- MongoDB connection strings
- JWT secrets

## Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Flask application entry point |
| `data/database_manager.py` | MongoDB CRUD operations |
| `ML/state_encoder.py` | FEN → Tensor conversion |
| `ML/agent.py` | Chess bot with search |
| `.github/workflows/ci.yml` | CI/CD pipeline |
| `requirements.txt` | Python dependencies |

## Development Status

⚠️ **Early Stage Project**: Most components are scaffolded with TODO markers. Implementation follows the architecture defined in `Chesster_Planning_Document.md`.
