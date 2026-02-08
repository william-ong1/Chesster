// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
// Tests for Training component

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Training } from '@/components/onboarding/Training'
import * as api from '@/services/api'

vi.mock('@/services/api')

const renderTraining = () => {
  return render(
    <BrowserRouter>
      <Training />
    </BrowserRouter>
  )
}

describe('Training', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays insufficient games message when user has less than 10 games', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 5 }
    })
    
    renderTraining()
    
    await waitFor(() => {
      expect(screen.getByText(/you currently have 5 games/i)).toBeInTheDocument()
      expect(screen.getByText(/please import more games/i)).toBeInTheDocument()
    })
  })

  it('shows training configuration when sufficient games exist', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 50 }
    })
    
    renderTraining()
    
    await waitFor(() => {
      expect(screen.getByLabelText(/model name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/epochs/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/batch size/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /start training/i })).toBeInTheDocument()
    })
  })

  it('starts training when start button is clicked', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 50 }
    })
    
    vi.mocked(api.trainingAPI.startTraining).mockResolvedValue({
      data: { job_id: 'job_123', success: true }
    })
    
    renderTraining()
    
    await waitFor(() => {
      const startButton = screen.getByRole('button', { name: /start training/i })
      fireEvent.click(startButton)
    })
    
    await waitFor(() => {
      expect(api.trainingAPI.startTraining).toHaveBeenCalledWith(
        expect.objectContaining({
          modelName: expect.any(String),
          epochs: expect.any(Number),
          batchSize: expect.any(Number),
          learningRate: expect.any(Number)
        })
      )
    })
  })

  it('displays training progress during training', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 50 }
    })
    
    vi.mocked(api.trainingAPI.startTraining).mockResolvedValue({
      data: { job_id: 'job_123', success: true }
    })
    
    vi.mocked(api.trainingAPI.getStatus).mockResolvedValue({
      data: {
        status: 'running',
        progress_percentage: 50,
        current_epoch: 25,
        total_epochs: 50,
        current_loss: 0.5,
        best_loss: 0.3
      }
    })
    
    renderTraining()
    
    const startButton = await screen.findByRole('button', { name: /start training/i })
    fireEvent.click(startButton)
    
    await waitFor(() => {
      expect(screen.getByText(/training/i)).toBeInTheDocument()
      expect(screen.getByText(/50%/i) || screen.getByText(/epoch/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('allows user to adjust training parameters', async () => {
    vi.mocked(api.statsAPI.getUserStats).mockResolvedValue({
      data: { games_count: 50 }
    })
    
    renderTraining()
    
    await waitFor(() => {
      const epochsSlider = screen.getByLabelText(/epochs/i)
      fireEvent.change(epochsSlider, { target: { value: 100 } })
      expect(epochsSlider).toHaveValue('100')
    })
  })
})
