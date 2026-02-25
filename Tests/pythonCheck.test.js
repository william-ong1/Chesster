const { getPythonBin } = require('./app/functions');
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

// Mock the dependencies
jest.mock('fs');
jest.mock('child_process');

describe('getPythonBin', () => {
  const mockRoot = '/test/project';
  
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('returns venv python when it exists', () => {
    fs.existsSync.mockImplementation((p) => 
      p === path.join(mockRoot, '.venv', 'bin', 'python')
    );

    const result = getPythonBin(mockRoot);
    
    expect(result).toBe(path.join(mockRoot, '.venv', 'bin', 'python'));
    expect(fs.existsSync).toHaveBeenCalledWith(
      path.join(mockRoot, '.venv', 'bin', 'python')
    );
  });

  test('returns venv python3 when python does not exist but python3 does', () => {
    fs.existsSync.mockImplementation((p) => 
      p === path.join(mockRoot, '.venv', 'bin', 'python3')
    );

    const result = getPythonBin(mockRoot);
    
    expect(result).toBe(path.join(mockRoot, '.venv', 'bin', 'python3'));
    expect(fs.existsSync).toHaveBeenCalledWith(
      path.join(mockRoot, '.venv', 'bin', 'python3')
    );
  });

  test('returns system python3 when venv does not exist and python3 is available', () => {
    fs.existsSync.mockReturnValue(false);
    execSync.mockImplementation((cmd) => {
      if (cmd === 'which python3') return '/usr/bin/python3';
      throw new Error('Command not found');
    });

    const result = getPythonBin(mockRoot);
    
    expect(result).toBe('python3');
    expect(execSync).toHaveBeenCalledWith('which python3', { encoding: 'utf-8' });
  });

  test('returns system python when venv and python3 do not exist but python is available', () => {
    fs.existsSync.mockReturnValue(false);
    execSync.mockImplementation((cmd) => {
      if (cmd === 'which python3') throw new Error('Command not found');
      if (cmd === 'which python') return '/usr/bin/python';
      throw new Error('Command not found');
    });

    const result = getPythonBin(mockRoot);
    
    expect(result).toBe('python');
    expect(execSync).toHaveBeenCalledWith('which python3', { encoding: 'utf-8' });
    expect(execSync).toHaveBeenCalledWith('which python', { encoding: 'utf-8' });
  });

  test('returns default python3 when no python is found anywhere', () => {
    fs.existsSync.mockReturnValue(false);
    execSync.mockImplementation(() => {
      throw new Error('Command not found');
    });

    const result = getPythonBin(mockRoot);
    
    expect(result).toBe('python3');
  });

  test('prefers venv python over venv python3', () => {
    // Both venv binaries exist
    fs.existsSync.mockReturnValue(true);

    const result = getPythonBin(mockRoot);
    
    // Should return the first one checked (python, not python3)
    expect(result).toBe(path.join(mockRoot, '.venv', 'bin', 'python'));
  });

  test('handles different root paths correctly', () => {
    const customRoot = '/custom/path';
    fs.existsSync.mockImplementation((p) => 
      p === path.join(customRoot, '.venv', 'bin', 'python')
    );

    const result = getPythonBin(customRoot);
    
    expect(result).toBe(path.join(customRoot, '.venv', 'bin', 'python'));
  });
});
