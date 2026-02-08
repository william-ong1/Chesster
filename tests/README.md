# Test Suite

## Code Owners
All teams are responsible for testing their components.

See root [CODEOWNERS](../CODEOWNERS) for review assignments.

## Structure
- `conftest.py` - Shared pytest fixtures
- `data/` - Data pipeline tests
- `ML/` - ML pipeline tests
- `backend/` - Backend API tests

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Component
```bash
pytest tests/data/ -v      # Data pipeline only
pytest tests/ML/ -v        # ML pipeline only
pytest tests/backend/ -v   # Backend API only
```

### With Coverage
```bash
pytest tests/ -v --cov=. --cov-report=html
```

## Fixtures Available
- `sample_pgn` - Example PGN game string
- `sample_fen` - Example board state in FEN notation

## CI/CD
Tests run automatically on push/PR via GitHub Actions.
See [.github/workflows/ci.yml](../.github/workflows/ci.yml)

## Next Steps
1. Implement TODOs in existing test files
2. Add integration tests for component interactions
3. Ensure >80% code coverage
4. Add performance benchmarks