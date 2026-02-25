const { dockerAvailable } = require('../app/functions');

const child_process = require('child_process');

jest.mock('child_process');

describe('dockerAvailable', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  test('returns true when docker info command succeeds', () => {
    // Mock execSync to not throw
    child_process.execSync.mockImplementation(() => 'some info');

    expect(dockerAvailable()).toBe(true);
    expect(child_process.execSync).toHaveBeenCalledWith('docker info', { stdio: 'ignore' });
  });

  test('returns false when docker info command throws', () => {
    // Mock execSync to throw error (simulate docker not available)
    child_process.execSync.mockImplementation(() => { throw new Error('command failed'); });

    expect(dockerAvailable()).toBe(false);
    expect(child_process.execSync).toHaveBeenCalledWith('docker info', { stdio: 'ignore' });
  });
});