// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Flag, RotateCcw, Loader2, AlertCircle } from 'lucide-react';
import { ChessPiece } from './ChessPiece';
import { agentAPI } from '../services/api';

type PieceType = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P';
type PieceColor = 'w' | 'b';

interface Piece {
  type: PieceType;
  color: PieceColor;
}

interface Square {
  row: number;
  col: number;
}

const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

export function ChessGame() {
  const navigate = useNavigate();
  const [fen, setFen] = useState(INITIAL_FEN);
  const [board, setBoard] = useState<(Piece | null)[][]>([]);
  const [selectedSquare, setSelectedSquare] = useState<Square | null>(null);
  const [legalMoves, setLegalMoves] = useState<string[]>([]);
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [isWaitingForBot, setIsWaitingForBot] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [gameResult, setGameResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [playerColor] = useState<'white' | 'black'>('white');
  const [thinkingTime, setThinkingTime] = useState<number | null>(null);
  const [currentTurn, setCurrentTurn] = useState<'w' | 'b'>('w');
  const [isInCheck, setIsInCheck] = useState(false);

  useEffect(() => {
    parseFENToBoard(INITIAL_FEN);
    
    // If bot plays white, make first move
    if (playerColor === 'black') {
      setTimeout(() => makeBotMove(), 500);
    }
  }, []);

  // Parse FEN string to 8x8 board array
  const parseFENToBoard = (fenString: string) => {
    const parts = fenString.split(' ');
    const position = parts[0];
    const turn = parts[1] as 'w' | 'b';
    
    setCurrentTurn(turn);
    
    const rows = position.split('/');
    const newBoard: (Piece | null)[][] = [];
    
    for (const row of rows) {
      const boardRow: (Piece | null)[] = [];
      for (const char of row) {
        if (char >= '1' && char <= '8') {
          // Empty squares
          const emptyCount = parseInt(char);
          for (let i = 0; i < emptyCount; i++) {
            boardRow.push(null);
          }
        } else {
          // Piece
          const color = char === char.toUpperCase() ? 'w' : 'b';
          boardRow.push({ type: char.toUpperCase() as PieceType, color });
        }
      }
      newBoard.push(boardRow);
    }
    
    setBoard(newBoard);
  };

  const makeBotMove = async () => {
    try {
      setIsWaitingForBot(true);
      setError(null);

      const response = await agentAPI.getMove(fen, 3); // depth 3 search

      const { move, move_san, thinking_time } = response.data;
      
      // Apply bot's move through backend
      const moveResponse = await agentAPI.makeMove(fen, move);
      const { new_fen, is_game_over, game_result, is_checkmate, is_stalemate, is_check } = moveResponse.data;
      
      // Update board with new position
      setFen(new_fen);
      parseFENToBoard(new_fen);
      setMoveHistory([...moveHistory, move_san]);
      setThinkingTime(thinking_time);
      setIsInCheck(is_check);

      // Check for game over
      if (is_game_over) {
        setGameOver(true);
        if (is_checkmate) {
          const winner = new_fen.split(' ')[1] === 'w' ? 'Black' : 'White';
          setGameResult(`Checkmate! ${winner} wins!`);
        } else if (is_stalemate) {
          setGameResult('Draw by stalemate');
        } else {
          setGameResult(game_result || 'Game Over');
        }
      }

    } catch (err: any) {
      console.error('Bot move error:', err);
      setError(err.response?.data?.error || 'Failed to get bot move');
    } finally {
      setIsWaitingForBot(false);
    }
  };

  const handleSquareClick = async (row: number, col: number) => {
    if (isWaitingForBot || gameOver || currentTurn !== (playerColor === 'white' ? 'w' : 'b')) return;

    const toSquare = `${String.fromCharCode(97 + col)}${8 - row}`;
    const piece = board[row][col];

    // If a square is already selected
    if (selectedSquare) {
      const fromSquare = `${String.fromCharCode(97 + selectedSquare.col)}${8 - selectedSquare.row}`;
      
      // Check if this is a legal move
      if (legalMoves.includes(toSquare)) {
        try {
          setError(null);

          // Construct UCI move
          const moveString = `${fromSquare}${toSquare}`;
          
          // Make move via backend
          const response = await agentAPI.makeMove(fen, moveString);
          const { new_fen, move_san, is_game_over, game_result, is_checkmate, is_stalemate, is_check } = response.data;
          
          // Update board
          setFen(new_fen);
          parseFENToBoard(new_fen);
          setMoveHistory([...moveHistory, move_san]);
          setSelectedSquare(null);
          setLegalMoves([]);
          setIsInCheck(is_check);

          // Check for game over
          if (is_game_over) {
            setGameOver(true);
            if (is_checkmate) {
              const winner = new_fen.split(' ')[1] === 'w' ? 'Black' : 'White';
              setGameResult(`Checkmate! ${winner} wins!`);
            } else if (is_stalemate) {
              setGameResult('Draw by stalemate');
            } else {
              setGameResult(game_result || 'Game Over');
            }
          } else {
            // Bot's turn
            setTimeout(() => makeBotMove(), 500);
          }

        } catch (err: any) {
          console.error('Move error:', err);
          setError(err.response?.data?.error || 'Invalid move');
          setSelectedSquare(null);
          setLegalMoves([]);
        }
      } else {
        // Try selecting new piece or deselect
        if (piece && piece.color === (playerColor === 'white' ? 'w' : 'b')) {
          setSelectedSquare({ row, col });
          await fetchLegalMoves(toSquare);
        } else {
          setSelectedSquare(null);
          setLegalMoves([]);
        }
      }
    } else {
      // Select a piece
      if (piece && piece.color === (playerColor === 'white' ? 'w' : 'b')) {
        setSelectedSquare({ row, col });
        await fetchLegalMoves(toSquare);
      }
    }
  };

  const fetchLegalMoves = async (square: string) => {
    try {
      const response = await agentAPI.getLegalMoves(fen, square);
      const { legal_moves } = response.data;
      
      // Extract destination squares from UCI moves (e.g., "e2e4" -> "e4")
      const destinations = legal_moves.map((move: string) => move.substring(2, 4));
      setLegalMoves(destinations);
    } catch (err: any) {
      console.error('Legal moves error:', err);
      setLegalMoves([]);
    }
  };

  const resetGame = () => {
    setFen(INITIAL_FEN);
    parseFENToBoard(INITIAL_FEN);
    setSelectedSquare(null);
    setLegalMoves([]);
    setMoveHistory([]);
    setGameOver(false);
    setGameResult(null);
    setError(null);
    setThinkingTime(null);
    setIsWaitingForBot(false);
    setIsInCheck(false);

    // If bot plays white, make first move
    if (playerColor === 'black') {
      setTimeout(() => makeBotMove(), 500);
    }
  };

  const resignGame = () => {
    setGameOver(true);
    setGameResult(`You resigned. ${playerColor === 'white' ? 'Black' : 'White'} wins!`);
  };

  const isSquareLegalMove = (row: number, col: number): boolean => {
    const square = `${String.fromCharCode(97 + col)}${8 - row}`;
    return legalMoves.includes(square);
  };

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-slate-600 hover:text-[#4A3B7A] transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </button>
        <div className="text-sm text-slate-600">
          Playing as {playerColor === 'white' ? 'White' : 'Black'} vs Your Mirror Bot
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-medium mb-1">Error</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Game Over Alert */}
      {gameOver && gameResult && (
        <div className="mb-6 bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
          <h2 className="text-2xl text-[#4A3B7A] mb-2">Game Over</h2>
          <p className="text-lg text-slate-700 mb-4">{gameResult}</p>
          <button
            onClick={resetGame}
            className="bg-[#4A3B7A] text-white px-6 py-2 rounded-lg hover:bg-[#3D3066] transition-colors"
          >
            Play Again
          </button>
        </div>
      )}

      <div className="grid lg:grid-cols-[1fr_400px] gap-8">
        {/* Chess Board */}
        <div className="space-y-4">
          {/* Opponent Info */}
          <div className="bg-white rounded-lg p-4 shadow-sm border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#4A3B7A] rounded-full flex items-center justify-center text-white font-bold">
                BOT
              </div>
              <div>
                <div className="text-sm font-medium">Mirror Bot ({playerColor === 'white' ? 'Black' : 'White'})</div>
                <div className="text-xs text-slate-500">
                  {isWaitingForBot ? 'Thinking...' : currentTurn !== (playerColor === 'white' ? 'w' : 'b') ? "Bot's turn" : "Waiting"}
                </div>
              </div>
            </div>
            {isWaitingForBot && (
              <Loader2 className="w-5 h-5 text-[#4A3B7A] animate-spin" />
            )}
          </div>

          {/* Board */}
          <div className="bg-white rounded-lg p-6 shadow-lg border border-slate-200">
            <div className="inline-block">
              {board.map((row, rowIndex) => (
                <div key={rowIndex} className="flex">
                  {row.map((piece, colIndex) => {
                    const isLight = (rowIndex + colIndex) % 2 === 0;
                    const isSelected = selectedSquare?.row === rowIndex && selectedSquare?.col === colIndex;
                    const isLegalMove = isSquareLegalMove(rowIndex, colIndex);
                    const isKingInCheck = isInCheck && piece?.type === 'K' && piece?.color === currentTurn;
                    
                    return (
                      <button
                        key={`${rowIndex}-${colIndex}`}
                        onClick={() => handleSquareClick(rowIndex, colIndex)}
                        disabled={isWaitingForBot || gameOver}
                        className={`w-20 h-20 flex items-center justify-center transition-all relative ${
                          isLight ? 'bg-[#F0D9B5]' : 'bg-[#B58863]'
                        } ${isSelected ? 'ring-4 ring-[#4A3B7A] ring-inset' : ''} ${
                          isKingInCheck ? 'bg-red-400' : ''
                        } ${!isWaitingForBot && !gameOver ? 'hover:opacity-80' : 'cursor-not-allowed opacity-75'}`}
                      >
                        {piece && (
                          <ChessPiece 
                            type={piece.type} 
                            color={piece.color} 
                          />
                        )}
                        {isLegalMove && (
                          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className={`${piece ? 'w-16 h-16 border-4 border-green-500 rounded-full' : 'w-4 h-4 bg-green-500 rounded-full opacity-50'}`}></div>
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* Player Info */}
          <div className="bg-white rounded-lg p-4 shadow-sm border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                YOU
              </div>
              <div>
                <div className="text-sm font-medium">You ({playerColor === 'white' ? 'White' : 'Black'})</div>
                <div className="text-xs text-slate-500">
                  {currentTurn === (playerColor === 'white' ? 'w' : 'b') ? 'Your turn' : 'Waiting for bot'}
                </div>
              </div>
            </div>
            {isInCheck && currentTurn === (playerColor === 'white' ? 'w' : 'b') && (
              <span className="text-red-600 text-sm font-medium">Check!</span>
            )}
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Game Controls */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
            <h3 className="text-sm tracking-wide text-purple-800 mb-4">GAME CONTROLS</h3>
            <div className="space-y-3">
              <button
                onClick={resetGame}
                disabled={isWaitingForBot}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-slate-200 rounded-lg hover:border-purple-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RotateCcw className="w-4 h-4" />
                New Game
              </button>
              <button 
                onClick={resignGame}
                disabled={gameOver || isWaitingForBot}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-50 text-red-600 border-2 border-red-200 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Flag className="w-4 h-4" />
                Resign
              </button>
            </div>
          </div>

          {/* Move History */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
            <h3 className="text-sm tracking-wide text-purple-800 mb-4">MOVE HISTORY</h3>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {moveHistory.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-4">No moves yet</p>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  {moveHistory.map((move, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm p-2 bg-slate-50 rounded">
                      <span className="text-slate-500 w-6">{Math.floor(index / 2) + 1}{index % 2 === 0 ? '.' : '...'}</span>
                      <span className="text-slate-700 font-mono">{move}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Bot Performance */}
          {thinkingTime !== null && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-sm tracking-wide text-purple-800 mb-3">LAST MOVE</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Thinking time</span>
                  <span className="text-[#4A3B7A] font-mono">{thinkingTime.toFixed(2)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Search depth</span>
                  <span className="text-[#4A3B7A]">3 ply</span>
                </div>
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
            <h3 className="text-sm tracking-wide text-purple-800 mb-3">TIPS</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Click a piece to select it. Green dots show legal moves. Click a highlighted square to move there. The bot uses alpha-beta search with your trained model to play moves similar to your style.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
