import { useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Flag, RotateCcw } from 'lucide-react';
import { ChessPiece } from './ChessPiece';

type PieceType = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P' | null;
type PieceColor = 'w' | 'b';

interface Piece {
  type: PieceType;
  color: PieceColor;
}

const initialBoard: (Piece | null)[][] = [
  [
    { type: 'R', color: 'b' }, { type: 'N', color: 'b' }, { type: 'B', color: 'b' }, { type: 'Q', color: 'b' },
    { type: 'K', color: 'b' }, { type: 'B', color: 'b' }, { type: 'N', color: 'b' }, { type: 'R', color: 'b' }
  ],
  Array(8).fill(null).map(() => ({ type: 'P' as PieceType, color: 'b' as PieceColor })),
  Array(8).fill(null),
  Array(8).fill(null),
  Array(8).fill(null),
  Array(8).fill(null),
  Array(8).fill(null).map(() => ({ type: 'P' as PieceType, color: 'w' as PieceColor })),
  [
    { type: 'R', color: 'w' }, { type: 'N', color: 'w' }, { type: 'B', color: 'w' }, { type: 'Q', color: 'w' },
    { type: 'K', color: 'w' }, { type: 'B', color: 'w' }, { type: 'N', color: 'w' }, { type: 'R', color: 'w' }
  ],
];

export function ChessGame() {
  const navigate = useNavigate();
  const [board, setBoard] = useState<(Piece | null)[][]>(initialBoard);
  const [selectedSquare, setSelectedSquare] = useState<[number, number] | null>(null);
  const [currentTurn, setCurrentTurn] = useState<PieceColor>('w');
  const [moves, setMoves] = useState<string[]>([]);
  const [capturedPieces, setCapturedPieces] = useState<{ w: PieceType[], b: PieceType[] }>({ w: [], b: [] });

  const handleSquareClick = (row: number, col: number) => {
    const piece = board[row][col];

    if (selectedSquare) {
      const [selectedRow, selectedCol] = selectedSquare;
      const selectedPiece = board[selectedRow][selectedCol];

      // Attempt to move
      if (selectedPiece && selectedPiece.color === currentTurn) {
        const newBoard = board.map(r => [...r]);
        
        // Capture piece if exists
        if (piece && piece.color !== currentTurn) {
          setCapturedPieces(prev => ({
            ...prev,
            [piece.color]: [...prev[piece.color], piece.type]
          }));
        }

        newBoard[row][col] = selectedPiece;
        newBoard[selectedRow][selectedCol] = null;
        setBoard(newBoard);
        
        // Record move
        const moveNotation = `${String.fromCharCode(97 + selectedCol)}${8 - selectedRow} to ${String.fromCharCode(97 + col)}${8 - row}`;
        setMoves([...moves, moveNotation]);
        
        setCurrentTurn(currentTurn === 'w' ? 'b' : 'w');
      }
      setSelectedSquare(null);
    } else {
      if (piece && piece.color === currentTurn) {
        setSelectedSquare([row, col]);
      }
    }
  };

  const resetGame = () => {
    setBoard(initialBoard);
    setSelectedSquare(null);
    setCurrentTurn('w');
    setMoves([]);
    setCapturedPieces({ w: [], b: [] });
  };

  const renderCapturedPiece = (type: PieceType, color: PieceColor) => {
    if (!type) return null;
    return (
      <div className="w-6 h-6 opacity-50">
        <ChessPiece type={type} color={color} />
      </div>
    );
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
          Playing as White vs Your Mirror Bot
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_400px] gap-8">
        {/* Chess Board */}
        <div className="space-y-4">
          {/* Opponent Info */}
          <div className="bg-white rounded-lg p-4 shadow-sm border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#4A3B7A] rounded-full flex items-center justify-center text-white">
                MB
              </div>
              <div>
                <div className="text-sm">Mirror Bot (Black)</div>
                <div className="text-xs text-slate-500">Similarity: 85%</div>
              </div>
            </div>
            <div className="flex gap-2">
              {capturedPieces.w.map((piece, i) => (
                <div key={i}>{renderCapturedPiece(piece, 'w')}</div>
              ))}
            </div>
          </div>

          {/* Board */}
          <div className="bg-white rounded-lg p-6 shadow-lg border border-slate-200">
            <div className="inline-block">
              {board.map((row, rowIndex) => (
                <div key={rowIndex} className="flex">
                  {row.map((piece, colIndex) => {
                    const isLight = (rowIndex + colIndex) % 2 === 0;
                    const isSelected = selectedSquare?.[0] === rowIndex && selectedSquare?.[1] === colIndex;
                    
                    return (
                      <button
                        key={`${rowIndex}-${colIndex}`}
                        onClick={() => handleSquareClick(rowIndex, colIndex)}
                        className={`w-20 h-20 flex items-center justify-center transition-all ${
                          isLight ? 'bg-[#F0D9B5]' : 'bg-[#B58863]'
                        } ${isSelected ? 'ring-4 ring-[#4A3B7A] ring-inset' : ''} hover:opacity-80`}
                      >
                        {piece && <ChessPiece type={piece.type!} color={piece.color} />}
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
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white">
                You
              </div>
              <div>
                <div className="text-sm">You (White)</div>
                <div className="text-xs text-slate-500">Your turn: {currentTurn === 'w' ? 'Yes' : 'No'}</div>
              </div>
            </div>
            <div className="flex gap-2">
              {capturedPieces.b.map((piece, i) => (
                <div key={i}>{renderCapturedPiece(piece, 'b')}</div>
              ))}
            </div>
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
                className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-slate-200 rounded-lg hover:border-purple-300 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                New Game
              </button>
              <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-50 text-red-600 border-2 border-red-200 rounded-lg hover:bg-red-100 transition-colors">
                <Flag className="w-4 h-4" />
                Resign
              </button>
            </div>
          </div>

          {/* Move History */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
            <h3 className="text-sm tracking-wide text-purple-800 mb-4">MOVE HISTORY</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {moves.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-4">No moves yet</p>
              ) : (
                moves.map((move, index) => (
                  <div key={index} className="flex items-center gap-3 text-sm p-2 bg-slate-50 rounded">
                    <span className="text-slate-500 w-6">{index + 1}.</span>
                    <span className="text-slate-700">{move}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Bot Insights */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <h3 className="text-sm tracking-wide text-purple-800 mb-3">BOT INSIGHTS</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Playing style</span>
                <span className="text-[#4A3B7A]">Aggressive</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Mimic accuracy</span>
                <span className="text-[#4A3B7A]">85%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Human-like</span>
                <span className="text-[#4A3B7A]">75%</span>
              </div>
            </div>
          </div>

          {/* Tips */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
            <h3 className="text-sm tracking-wide text-purple-800 mb-3">TIPS</h3>
            <p className="text-sm text-slate-600">
              Click a piece to select it, then click a destination square to move. The bot will respond with moves similar to your typical playing style.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}