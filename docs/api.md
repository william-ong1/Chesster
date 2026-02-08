# Chesster API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication Endpoints

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "string",
  "token": "jwt_token"
}
```

### POST /api/auth/login
User login with credentials.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token",
  "user_id": "string"
}
```

## Data Upload Endpoints

### POST /api/upload-pgn
Upload chess game data in PGN format.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "user_id": "string",
  "pgn_data": "string",
  "metadata": {
    "source": "chess.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "games_processed": 10,
  "message": "Successfully processed 10 games"
}
```

## Training Endpoints

### POST /api/train-model
Initiate model training for a user.

**Request Body:**
```json
{
  "user_id": "string",
  "architecture": "3_layer_nn",
  "hyperparameters": {
    "learning_rate": 0.001,
    "epochs": 50
  }
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "uuid",
  "estimated_time": 300
}
```

### GET /api/training-status/<job_id>
Get training job status and progress.

**Response:**
```json
{
  "status": "training",
  "progress": 0.65,
  "epoch": 33,
  "loss": 0.145,
  "model_id": "model_uuid"
}
```

## Gameplay Endpoints

### POST /api/get-move
Get the bot's move for a given board state.

**Request Body:**
```json
{
  "user_id": "string",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "model_id": "optional_model_id"
}
```

**Response:**
```json
{
  "move": "e5",
  "evaluation": 0.15,
  "thinking_time": 0.42
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "error": "Error message description"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
