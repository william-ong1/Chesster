// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper
, Lebam Amare, Raghav Ramesh, and Danyuan Wang                      // Vitest configuration for frontend tests

import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.ts',
        '*.config.js',
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
})