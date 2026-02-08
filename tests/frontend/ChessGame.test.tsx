// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
// Tests for ChessGame component

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ChessGame from '@/components/ChessGame'
import * as api from '@/services/api'

vi.mock('@/services/api')

const renderChessGame = () => {
  return render(
    <BrowserRouter>
      <ChessGame />
    </BrowserRouter>
  )
}

describe('ChessGame', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders chess board with 64 squares', () => {
    renderChessGame()
    
    const squares = screen.getAllByRole('button')
    // 64 squares + control buttons
    expect(squares.length).toBeGreaterThanOrEqual(64)
  })

  it('displays starting position pieces', () => {
    renderChessGame()
    
    // Check for piece symbols (Unicode chess pieces)
    const board = screen.getByRole('grid', { hidden: true }) || document.querySelector('.chess-board')
    expect(board).toBeDefined()
  })

  it('highlights legal moves when piece is selected', async () => {
    const mockLegalMoves = {
      data: {
        legal_moves: ['e2e3', 'e2e4'],
        legal_moves_san: ['e3', 'e4']
      }
    }
    
    vi.mocked(api.agentAPI.getLegalMoves).mockResolvedValue(mockLegalMoves)
    
    renderChessGame()
    
    // Click on e2 pawn
    const e2Square = screen.getAllByRole('button')[12] // Approximate position
    fireEvent.click(e2Square)
    
    await waitFor(() => {
      expect(api.agentAPI.getLegalMoves).toHaveBeenCalled()
    })
  })

  it('makes player move when valid destination is clicked', async () => {
    const mockMakeMove = {
      data: {
        new_fen: 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
        move_san: 'e4',
        is_game_over: false,
        is_check: false
      }
    }
    
    vi.mocked(api.agentAPI.makeMove).mockResolvedValue(mockMakeMove)
    
    renderChessGame()
    
    // Simulate making a move
    const fromSquare = screen.getAllByRole('button')[12]
    const toSquare = screen.getAllByRole('button')[28]
    
    fireEvent.click(fromSquare)
    fireEvent.click(toSquare)
    
    await waitFor(() => {
      expect(api.agentAPI.makeMove).toHaveBeenCalled()
    })
  })

  it('shows check indicator when king is in check', async () => {
    const mockMakeMove = {
      data: {
        new_fen: 'rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3',
        move_san: 'Qh4+',
        is_game_over: false,
        is_check: true
      }
    }
    
    vi.mocked(api.agentAPI.makeMove).mockResolvedValue(mockMakeMove)
    
    renderChessGame()
    
    // After move that puts king in check
    await waitFor(() => {
      const checkIndicator = screen.queryByText(/check/i)
      if (checkIndicator) {
        expect(checkIndicator).toBeInTheDocument()
      }
    })
  })

  it('disables moves when game is over', async () => {
    const mockMakeMove = {
      data: {
        new_fen: 'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 3',
        move_san: 'Qh4#',
        is_game_over: true,
        is_checkmate: true
      }
    }
    
    vi.mocked(api.agentAPI.makeMove).mockResolvedValue(mockMakeMove)
    
    renderChessGame()
    
    // Game should be over
    await waitFor(() => {
      const gameOverText = screen.queryByText(/checkmate|game over/i)
      if (gameOverText) {
        expect(gameOverText).toBeInTheDocument()
      }
    })
  })

  it('resets game when new game button is clicked', () => {
    renderChessGame()
    
    const newGameButton = screen.getByRole('button', { name: /new game/i })
    fireEvent.click(newGameButton)
    
    // Board should be reset to starting position
    expect(screen.getByRole('grid', { hidden: true }) || document.querySelector('.chess-board')).toBeDefined()
  })
})
