# Data Pipeline Component

## Code Owners
**Primary Team:** @danyuanwang @lbmlkCodes @masont7

See root [CODEOWNERS](../CODEOWNERS) for review assignments.

## Components
- `PGN_cleaner.py` - Sanitize raw PGN data
- `PGN_to_board_state.py` - Convert PGN to FEN board states
- `pgn_downloader.py` - Download games from Chess.com/Lichess
- `pgn_parser.py` - Parse PGN to structured data
- `game_validator.py` - Filter low-quality games
- `move_extractor.py` - Extract board states and moves
- `database_manager.py` - MongoDB CRUD operations

## Data Flow
1. Download/Upload PGN → `pgn_downloader.py` or API
2. Clean PGN → `PGN_cleaner.py`
3. Parse to structured data → `pgn_parser.py`
4. Validate game quality → `game_validator.py`
5. Extract training data → `move_extractor.py`
6. Store in MongoDB → `database_manager.py`

## Status
🚧 Scaffolded - implementation in progress

## Next Steps for Data Team
1. Complete `PGN_cleaner.py` sanitization logic
2. Implement `PGN_to_board_state.py` conversion
3. Add Chess.com/Lichess API integration to `pgn_downloader.py`
4. Test MongoDB integration end-to-end
5. Write unit tests in `tests/data/`
