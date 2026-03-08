const { getPythonBin } = require('../app/functions');
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

// Mock the dependencies
jest.mock('fs');
jest.mock('child_process');

/** Mirror implementation path logic so tests pass on both Unix and Windows. */
function venvPaths(root) {
  const isWin = process.platform === 'win32';
  const scriptsDir = isWin ? 'Scripts' : 'bin';
  const pyName = isWin ? 'python.exe' : 'python';
  const py3Name = isWin ? 'python.exe' : 'python3';
  return {
    venvPy: path.join(root, '.venv', scriptsDir, pyName),
    venvPy3: path.join(root, '.venv', scriptsDir, py3Name),
  };
}

describe('getPythonBin', () => {
  const mockRoot = '/test/project';

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('returns venv python when it exists', () => {
    const { venvPy } = venvPaths(mockRoot);
    fs.existsSync.mockImplementation((p) => p === venvPy);

    const result = getPythonBin(mockRoot);

    expect(result).toBe(venvPy);
    expect(fs.existsSync).toHaveBeenCalledWith(venvPy);
  });

  test('returns venv python3 when python does not exist but python3 does', () => {
    const { venvPy, venvPy3 } = venvPaths(mockRoot);
    // On Windows venv has only Scripts/python.exe, so venvPy === venvPy3; verify we return it when present.
    if (venvPy === venvPy3) {
      fs.existsSync.mockImplementation((p) => p === venvPy);
      const result = getPythonBin(mockRoot);
      expect(result).toBe(venvPy);
      return;
    }
    fs.existsSync.mockImplementation((p) => p !== venvPy && p === venvPy3);

    const result = getPythonBin(mockRoot);

    expect(result).toBe(venvPy3);
    expect(fs.existsSync).toHaveBeenCalledWith(venvPy);
    expect(fs.existsSync).toHaveBeenCalledWith(venvPy3);
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

    const { venvPy } = venvPaths(mockRoot);
    expect(result).toBe(venvPy);
  });

  test('handles different root paths correctly', () => {
    const customRoot = '/custom/path';
    const { venvPy } = venvPaths(customRoot);
    fs.existsSync.mockImplementation((p) => p === venvPy);

    const result = getPythonBin(customRoot);

    expect(result).toBe(venvPy);
  });
});
