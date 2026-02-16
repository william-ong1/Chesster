# Configuration

## Code Owners
Shared responsibility - changes require approval from at least one team lead.

## Files
- `config.py` - Flask configuration classes (Development, Testing, Production)
- `.env.example` - Environment variable template

## Usage

### Development
```python
from config.config import DevelopmentConfig
app.config.from_object(DevelopmentConfig)
```

### Environment Variables
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
# Edit .env with your values
```

**Required Variables:**
- `MONGODB_URI` - MongoDB connection string
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key

**Optional Variables:**
- `FLASK_ENV` - development/testing/production
- `FLASK_PORT` - Backend port (default: 5000)
- `STOCKFISH_PATH` - Path to Stockfish binary

## Security
⚠️ **Never commit `.env` files to git!**

The `.env` file is in `.gitignore` to prevent accidental commits.
