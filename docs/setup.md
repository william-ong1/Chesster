# Setup Instructions for Chesster

## Prerequisites
- Python 3.10+
- MongoDB 6.0+
- Stockfish chess engine (optional, for training)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/william-ong1/Chesster.git
cd Chesster
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp config/.env.example .env
# Edit .env with your settings
```

### 5. Start MongoDB
```bash
# On macOS with Homebrew:
brew services start mongodb-community

# On Linux:
sudo systemctl start mongod

# Or use Docker:
docker run -d -p 27017:27017 --name chesster-mongo mongo:6.0
```

### 6. Run Backend Server
```bash
cd backend
python app.py
```

The API will be available at `http://localhost:5000`

## Running Tests
```bash
pytest tests/ -v
```

## Development Workflow
See [Development Guide](development.md) for detailed instructions.

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongosh --eval "db.adminCommand({ping: 1})"`
- Check connection string in `.env`

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change `FLASK_PORT` in `.env`
- Or kill existing process: `lsof -ti:5000 | xargs kill -9`
