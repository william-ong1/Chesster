# Chesster Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend (Planned - React + TypeScript)"]
        UI[Chess UI<br/>React Components]
        Auth[Authentication<br/>Login/Register]
        Upload[File Upload<br/>PGN Import]
        Game[Chess Board<br/>Gameplay Interface]
        Training[Training Dashboard<br/>Progress Monitor]
    end

    subgraph Backend["Backend API (Flask/FastAPI)"]
        FlaskApp[Flask App<br/>app.py]
        
        subgraph API["API Endpoints"]
            AuthAPI[/api/auth/*<br/>JWT Authentication]
            UploadAPI[/api/upload-pgn<br/>Data Upload]
            TrainAPI[/api/train-model<br/>Training Control]
            StatusAPI[/api/training-status<br/>Progress Polling]
            MoveAPI[/api/get-move<br/>Chess Agent]
        end
    end

    subgraph DataPipeline["Data Pipeline"]
        Downloader[PGN Downloader<br/>Chess.com/Lichess APIs]
        Cleaner[PGN Cleaner<br/>Sanitize Data]
        Parser[PGN Parser<br/>python-chess]
        Validator[Game Validator<br/>Quality Filtering]
        Extractor[Move Extractor<br/>FEN + Moves]
        DBManager[Database Manager<br/>MongoDB Operations]
    end

    subgraph MLPipeline["ML Pipeline"]
        Orchestrator[Training Orchestrator<br/>Job Management]
        Encoder[State Encoder<br/>FEN → 14×8×8 Tensor]
        Dataset[Chess Dataset<br/>PyTorch DataLoader]
        
        subgraph Training["Training"]
            Trainer[Trainer<br/>training.py]
            Models[Model Architectures<br/>3-layer NN, CNN, ResNet]
            Stockfish[Stockfish<br/>Position Evaluation]
        end
        
        subgraph Inference["Inference"]
            Agent[Chess Agent<br/>agent.py]
            Search[Alpha-Beta Pruning<br/>Depth 3-5]
            Cache[Model Cache<br/>LRU Cache]
        end
        
        Evaluator[Model Evaluator<br/>MSE Metrics]
    end

    subgraph Database["MongoDB"]
        GameData[(game_data<br/>Collection)]
        ModelsDB[(models<br/>Collection)]
        UsersDB[(users<br/>Collection)]
        GridFS[(GridFS<br/>Large Models >16MB)]
    end

    %% Frontend to Backend connections
    UI --> FlaskApp
    Auth --> AuthAPI
    Upload --> UploadAPI
    Game --> MoveAPI
    Training --> TrainAPI
    Training --> StatusAPI

    %% Backend to Data Pipeline
    UploadAPI --> Cleaner
    Downloader --> Cleaner
    Cleaner --> Parser
    Parser --> Validator
    Validator --> Extractor
    Extractor --> DBManager
    DBManager --> GameData

    %% Backend to ML Pipeline
    TrainAPI --> Orchestrator
    Orchestrator --> DBManager
    DBManager --> Dataset
    Dataset --> Encoder
    Encoder --> Trainer
    Trainer --> Models
    Models --> Stockfish
    Stockfish --> Trainer
    Trainer --> DBManager
    DBManager --> ModelsDB
    DBManager --> GridFS

    %% Inference Flow
    MoveAPI --> Agent
    Agent --> Cache
    Cache --> ModelsDB
    Cache --> GridFS
    Agent --> Search
    Search --> Agent
    Agent --> MoveAPI

    %% Authentication
    AuthAPI --> UsersDB

    %% Evaluation
    Trainer --> Evaluator
    Evaluator --> ModelsDB

    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef backend fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef ml fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef db fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    class UI,Auth,Upload,Game,Training frontend
    class FlaskApp,AuthAPI,UploadAPI,TrainAPI,StatusAPI,MoveAPI backend
    class Downloader,Cleaner,Parser,Validator,Extractor,DBManager data
    class Orchestrator,Encoder,Dataset,Trainer,Models,Stockfish,Agent,Search,Cache,Evaluator ml
    class GameData,ModelsDB,UsersDB,GridFS db
```

## Architecture Overview

### Data Flow Paths

#### 1. **Data Upload & Processing Flow**
```
User Upload → UploadAPI → PGN Cleaner → PGN Parser → Game Validator 
→ Move Extractor → Database Manager → MongoDB (game_data)
```

#### 2. **Training Flow**
```
TrainAPI → Orchestrator → Database Manager → Chess Dataset → State Encoder 
→ Trainer → Model Architecture → Stockfish Evaluation → Save to MongoDB
```

#### 3. **Inference Flow**
```
User Move Request → MoveAPI → Chess Agent → Model Cache → Load Model 
→ Alpha-Beta Search → Evaluate Positions → Return Best Move
```

#### 4. **Authentication Flow**
```
User → AuthAPI → Hash/Verify Password → JWT Token → MongoDB (users)
```

## Component Details

### Frontend (Planned)
- **Technology**: React + TypeScript
- **Features**: Chess board UI, PGN upload, training dashboard, game replay
- **Communication**: REST API calls to backend

### Backend API
- **Technology**: Flask/FastAPI + Python 3.10+
- **Endpoints**: Auth, Upload, Training, Agent
- **Responsibility**: Request routing, authentication, orchestration

### Data Pipeline
- **Input**: PGN files from Chess.com, Lichess, or manual upload
- **Processing**: Clean → Parse → Validate → Extract → Store
- **Output**: Board states (FEN) with moves in MongoDB
- **Key Libraries**: python-chess, pymongo

### ML Pipeline
- **Training**: Supervised learning with Stockfish guidance
- **Model Type**: Evaluation networks (output position scores)
- **Search**: Alpha-beta pruning to select moves
- **State Encoding**: 14×8×8 tensors (12 piece channels + 2 metadata)
- **Key Libraries**: PyTorch, python-chess

### Database
- **Technology**: MongoDB 6.0+
- **Collections**: 
  - `game_data`: User games with board states
  - `models`: Trained models metadata
  - `users`: User accounts and auth
- **GridFS**: Large model files (>16MB)
- **Indexes**: Compound indexes on (user_id, game_id) and (user_id, is_active)

## Key Design Decisions

1. **Evaluation Networks vs Policy Networks**
   - Models output position evaluations, not direct moves
   - Allows alpha-beta search for better move selection
   - More interpretable than pure policy networks

2. **MongoDB with GridFS**
   - Flexible schema for game data
   - GridFS handles large model files
   - Easy to scale horizontally

3. **Separate Training and Inference**
   - Training orchestrator queues async jobs
   - Agent uses cached models for fast inference
   - Clear separation of concerns

4. **Weighted Training**
   - Combines player move frequencies + Stockfish evaluations
   - Balances playstyle mimicry with chess strength
   - Configurable weighting for tuning

## Integration Points

- **Data → ML**: MongoDB game_data provides training data
- **ML → Backend**: Agent provides move generation service
- **Backend → Data**: Upload API triggers data processing
- **Backend → ML**: Training API triggers model training
- **Frontend → Backend**: REST API for all operations

## Status

🚧 **Current Phase**: Scaffolding complete, implementation in progress  
📅 **Next Milestone**: Feb 10 - Working data pipeline, ML training, basic API
