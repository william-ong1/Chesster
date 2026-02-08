// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper
, Lebam Amare, Raghav Ramesh, and Danyuan Wang                      // Test setup file for Vitest

import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

global.localStorage = localStorageMock as any