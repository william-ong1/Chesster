// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
// Tests for ImportGames component

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ImportGames } from '@/components/onboarding/ImportGames'
import * as api from '@/services/api'

vi.mock('@/services/api')

const renderImportGames = () => {
  return render(
    <BrowserRouter>
      <ImportGames />
    </BrowserRouter>
  )
}

describe('ImportGames', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload interface', () => {
    renderImportGames()
    
    expect(screen.getByText(/import your games/i)).toBeInTheDocument()
    expect(screen.getByText(/upload pgn file/i)).toBeInTheDocument()
  })

  it('uploads PGN file successfully', async () => {
    vi.mocked(api.uploadAPI.uploadPGN).mockResolvedValue({
      data: { success: true, games_stored: 5 }
    })
    
    renderImportGames()
    
    const file = new File(['[Event "Test"]\n1. e4 e5'], 'test.pgn', { type: 'application/x-chess-pgn' })
    const input = screen.getByLabelText(/drop your pgn file/i, { exact: false }).querySelector('input')
    
    if (input) {
      fireEvent.change(input, { target: { files: [file] } })
      
      await waitFor(() => {
        expect(api.uploadAPI.uploadPGN).toHaveBeenCalledWith(file)
      })
    }
  })

  it('displays error message on upload failure', async () => {
    vi.mocked(api.uploadAPI.uploadPGN).mockRejectedValue({
      response: { data: { message: 'Invalid PGN format' } }
    })
    
    renderImportGames()
    
    const file = new File(['invalid pgn'], 'test.pgn', { type: 'application/x-chess-pgn' })
    const input = screen.getByLabelText(/drop your pgn file/i, { exact: false }).querySelector('input')
    
    if (input) {
      fireEvent.change(input, { target: { files: [file] } })
      
      await waitFor(() => {
        expect(screen.getByText(/invalid pgn format/i) || screen.getByText(/failed/i)).toBeInTheDocument()
      })
    }
  })

  it('shows uploading state while file is processing', async () => {
    let resolveUpload: any
    vi.mocked(api.uploadAPI.uploadPGN).mockReturnValue(
      new Promise(resolve => { resolveUpload = resolve })
    )
    
    renderImportGames()
    
    const file = new File(['[Event "Test"]\n1. e4 e5'], 'test.pgn', { type: 'application/x-chess-pgn' })
    const input = screen.getByLabelText(/drop your pgn file/i, { exact: false }).querySelector('input')
    
    if (input) {
      fireEvent.change(input, { target: { files: [file] } })
      
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument()
      })
      
      // Resolve the upload
      resolveUpload({ data: { success: true } })
    }
  })
})
