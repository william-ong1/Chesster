// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
// Tests for Dashboard component

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '@/components/Dashboard'
import * as api from '@/services/api'

vi.mock('@/services/api')

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays user statistics', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: {
        games_count: 47,
        total_moves: 1234,
        avg_game_length: 26
      }
    })
    
    vi.mocked(api.trainingAPI.getModels).mockResolvedValue({
      data: { models: [] }
    })
    
    renderDashboard()
    
    await waitFor(() => {
      expect(screen.getByText(/47/i)).toBeInTheDocument()
    })
  })

  it('displays trained models', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 47 }
    })
    
    vi.mocked(api.trainingAPI.getModels).mockResolvedValue({
      data: {
        models: [
          { model_id: 'model1', model_name: 'My Bot', epochs: 50, is_active: true },
          { model_id: 'model2', model_name: 'Bot v2', epochs: 100, is_active: false }
        ]
      }
    })
    
    renderDashboard()
    
    await waitFor(() => {
      expect(screen.getByText(/my bot/i)).toBeInTheDocument()
      expect(screen.getByText(/bot v2/i)).toBeInTheDocument()
    })
  })

  it('activates model when activate button is clicked', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 47 }
    })
    
    vi.mocked(api.trainingAPI.getModels).mockResolvedValue({
      data: {
        models: [
          { model_id: 'model1', model_name: 'My Bot', is_active: false }
        ]
      }
    })
    
    vi.mocked(api.trainingAPI.activateModel).mockResolvedValue({
      data: { success: true }
    })
    
    renderDashboard()
    
    await waitFor(() => {
      const activateButton = screen.getAllByRole('button').find(
        btn => btn.textContent?.includes('Activate') || btn.textContent?.includes('Use')
      )
      if (activateButton) {
        fireEvent.click(activateButton)
      }
    })
    
    await waitFor(() => {
      expect(api.trainingAPI.activateModel).toHaveBeenCalledWith('model1')
    })
  })

  it('shows active indicator on currently active model', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 47 }
    })
    
    vi.mocked(api.trainingAPI.getModels).mockResolvedValue({
      data: {
        models: [
          { model_id: 'model1', model_name: 'Active Bot', is_active: true }
        ]
      }
    })
    
    renderDashboard()
    
    await waitFor(() => {
      expect(screen.getByText(/active/i)).toBeInTheDocument()
    })
  })
})
