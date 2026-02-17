/* eslint-disable prettier/prettier */
import {defineConfig} from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.ts', 'tests/**/*.tsx'],
    coverage: {
      enabled: true,
      provider: 'v8',
      include: ['./**/*.{ts,tsx}'],
      exclude: [
        // files/patterns to ignore
        './**/index.tsx',
        './**/setupTests.ts',
        './**/*.d.{ts,tsx}',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
      reporter: ['text', 'html', 'json'],
    },
  },
});
