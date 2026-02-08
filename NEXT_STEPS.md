# Chesster Development - Next Steps

## ✅ Completed
- [x] Complete project scaffolding
- [x] Copyright headers added to all code files
- [x] CODEOWNERS references in each folder
- [x] CI/CD pipeline configured
- [x] Test infrastructure setup
- [x] Documentation structure

---

## 🎯 Immediate Next Steps (Week of Feb 7-14)

### 🗄️ Data Team (@danyuanwang @lbmlkCodes @masont7)

#### Priority 1: Core Data Pipeline
1. **Implement `PGN_cleaner.py`**
   - Remove comments and extraneous text
   - Validate PGN format
   - Handle multiple games in one file
   - Test with real Chess.com/Lichess exports

2. **Complete `PGN_to_board_state.py`**
   - Use `pgn_parser.py` and `move_extractor.py` (already scaffolded)
   - Return list of FEN strings
   - Add error handling for invalid moves

3. **Test MongoDB Integration**
   ```bash
   # Start MongoDB
   brew services start mongodb-community
   
   # Test database_manager.py
   python -c "from data.database_manager import DatabaseManager; db = DatabaseManager(); print('Connected!')"
   ```

4. **Write Tests**
   - Complete TODOs in `tests/data/test_data_pipeline.py`
   - Test with sample PGN files
   - Verify data validation logic

#### Priority 2: Platform Integration
5. **Implement `pgn_downloader.py` APIs**
   - Chess.com: https://www.chess.com/news/view/published-data-api
   - Lichess: https://lichess.org/api
   - Handle rate limiting
   - Add pagination support

---

### 🤖 ML Team (@RaghavRamesh125 @William-Ong1 @danyuanwang @lbmlkCodes @shreyanmitra)

#### Priority 1: Training Pipeline
1. **Complete `training.py`**
   - Integrate `StateEncoder` and `ChessDataset` (already created)
   - Implement training loop with PyTorch
   - Use weighted loss: player moves + Stockfish evaluations
   - Save checkpoints during training
   
   ```python
   from ML.state_encoder import StateEncoder
   from ML.chess_dataset import ChessDataset
   from torch.utils.data import DataLoader
   
   # Your training loop here
   ```

2. **Implement Alpha-Beta Search in `agent.py`**
   - Load model from cache
   - Generate legal moves with python-chess
   - Evaluate positions with trained network
   - Return best move after search
   - Target: depth 3-5 search

3. **Complete `evaluate_model.py`**
   - Calculate MSE between model predictions and player moves
   - Test on validation set
   - Save metrics to MongoDB

4. **Install Stockfish**
   ```bash
   # macOS
   brew install stockfish
   
   # Linux
   sudo apt-get install stockfish
   
   # Verify installation
   which stockfish
   ```

#### Priority 2: Model Architectures
5. **Add More Architectures**
   - Create `CNN_model.py` in `model_architectures/`
   - Create `ResNet_model.py` for deeper networks
   - Follow pattern from `3_layer_nn.py`

6. **Write Tests**
   - Complete TODOs in `tests/ML/test_ml_components.py`
   - Test state encoding thoroughly
   - Verify model cache eviction

---

### 🌐 Backend Team (All Members)

#### Priority 1: API Implementation
1. **Complete Backend Endpoints**
   - Finish TODOs in `backend/api/upload.py`
   - Finish TODOs in `backend/api/training.py`
   - Finish TODOs in `backend/api/agent.py`

2. **Implement JWT Authentication**
   - Complete `backend/auth/authentication.py`
   - Use bcrypt for password hashing
   - Generate JWT tokens with `flask-jwt-extended`
   
   ```python
   import bcrypt
   from flask_jwt_extended import create_access_token
   
   # Hash password
   password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   
   # Create token
   token = create_access_token(identity=user_id)
   ```

3. **Connect Components**
   - Import data pipeline in `upload.py`
   - Import ML orchestrator in `training.py`
   - Import agent in `agent.py`

4. **Test APIs Locally**
   ```bash
   cd backend
   python app.py
   
   # In another terminal
   curl http://localhost:5000/health
   ```

#### Priority 2: API Testing
5. **Write API Tests**
   - Complete `tests/backend/test_api.py`
   - Use Flask test client
   - Test auth flow (register → login → protected endpoint)

---

### 👥 All Teams - Integration Tasks

#### Priority 1: Environment Setup
1. **Setup Local Development Environment**
   ```bash
   # Clone repo (if not done)
   git clone https://github.com/william-ong1/Chesster.git
   cd Chesster
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment
   cp config/.env.example .env
   # Edit .env with your MongoDB URI
   ```

2. **Start MongoDB**
   - Install MongoDB 6.0+
   - Start service
   - Verify connection

3. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

#### Priority 2: Documentation
4. **Update Documentation**
   - Add implementation notes to your team's README
   - Document any design decisions
   - Update API docs if endpoints change

5. **Git Workflow**
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name
   
   # Make changes, test locally
   pytest tests/ -v
   
   # Commit with clear messages
   git add .
   git commit -m "feat: implement PGN cleaning logic"
   
   # Push and create PR
   git push origin feature/your-feature-name
   ```

---

## 📅 Milestone Timeline (from Planning Doc)

### Week of Feb 10 (Milestone 04)
**Goal:** Finish Data Pipeline, ML Pipeline, and UI basics

- [ ] MongoDB setup complete
- [ ] Data pipeline processes sample games
- [ ] ML can train on single user's data
- [ ] Backend API functional for basic operations
- [ ] All tests passing in CI

### Week of Feb 17 (Milestone 05 - Beta Release)
**Goal:** Component integration + usability testing

- [ ] Data → ML → Backend fully integrated
- [ ] Can upload PGN → train model → get moves
- [ ] Beta testers can use the system
- [ ] Find and fix integration bugs

---

## 🛠️ Development Best Practices

### Code Quality
- Run `flake8` before committing: `flake8 . --max-line-length=127`
- Use type hints on all functions
- Add docstrings to public methods
- Follow patterns from existing scaffolding

### Testing
- Write tests as you implement features
- Aim for >80% code coverage
- Use fixtures from `tests/conftest.py`
- Test edge cases and error conditions

### Commits
- Use conventional commit format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `test:` for tests
  - `refactor:` for refactoring

### Pull Requests
- Reference CODEOWNERS for reviewers
- Include description of changes
- Ensure CI passes before requesting review
- Respond to review comments promptly

---

## 🆘 Troubleshooting

### MongoDB Won't Connect
```bash
# Check if running
mongosh --eval "db.adminCommand({ping: 1})"

# Start service (macOS)
brew services start mongodb-community

# Start service (Linux)
sudo systemctl start mongod
```

### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/data/test_data_pipeline.py::TestPGNParser::test_parse_single_game -v
```

### Port 5000 In Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in .env
FLASK_PORT=5001
```

---

## 📚 Key Resources

- [Project Planning Doc](Chesster_Planning_Document.md)
- [Architecture Overview](docs/structure.md)
- [API Documentation](docs/api.md)
- [Setup Guide](docs/setup.md)
- [python-chess docs](https://python-chess.readthedocs.io/)
- [PyTorch tutorials](https://pytorch.org/tutorials/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [MongoDB Python driver](https://pymongo.readthedocs.io/)

---

## 📞 Team Communication

- **Discord**: Daily updates and questions
- **Scheduled Meetings**:
  - Tuesday & Thursday (class time)
  - Sunday 3 PM
- **Status Reports**: Update every Tuesday in `StatusReports/`

---

## 🎉 Quick Wins to Start

Each team member can pick one of these to get started immediately:

1. **Write a test** - Pick any TODO in test files and implement it
2. **Implement a helper function** - Small utility functions in data/ML
3. **Add error handling** - Improve error messages in existing code
4. **Update documentation** - Clarify any confusing parts
5. **Setup environment** - Get MongoDB running and tests passing locally

**Remember:** It's okay to ask questions in Discord! This is a learning experience. 🚀
