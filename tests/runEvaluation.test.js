/**
 * Tests that runEvaluationAfterTraining:
 * 1. Invokes prediction_generator (via Docker) when test CSVs and model exist
 * 2. Pipes evaluation stdout to console.log
 * 3. Sends evaluation output to the UI via send()
 */

const path = require('path');
const { runEvaluationAfterTraining } = require('../app/runEvaluation');

describe('runEvaluationAfterTraining', () => {
  const baseOpts = {
    outputDir: '/tmp/session_123',
    username: 'testplayer',
    latestModelPath: '/tmp/maia/final_models/session/config/maia-1900.pb.gz',
    finalModelsDir: '/tmp/maia/final_models',
    maiaDir: '/tmp/maia',
    imageName: 'chess-mimic-training-amd64',
    root: '/tmp/chesster',
    send: jest.fn(),
  };

  let mockSpawn;
  let mockProcess;
  let consoleLogSpy;

  beforeEach(() => {
    jest.clearAllMocks();
    mockProcess = {
      stdout: { on: jest.fn() },
      stderr: { on: jest.fn() },
      on: jest.fn(),
    };
    mockSpawn = jest.fn(() => mockProcess);
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
  });

  test('skips evaluation when no test CSVs exist', async () => {
    const deps = {
      spawn: mockSpawn,
      fs: { existsSync: jest.fn(() => false) },
      path,
    };

    await runEvaluationAfterTraining(baseOpts, deps);

    expect(mockSpawn).not.toHaveBeenCalled();
    expect(baseOpts.send).not.toHaveBeenCalledWith(
      'train',
      'Running evaluation on test set...',
      expect.any(Number),
      'status'
    );
  });

  test('skips evaluation when no trained model exists', async () => {
    const deps = {
      spawn: mockSpawn,
      fs: {
        existsSync: jest.fn((p) =>
          p.includes('test_white') || p.includes('test_black')
        ),
      },
      path,
    };

    await runEvaluationAfterTraining(
      { ...baseOpts, latestModelPath: null },
      deps
    );

    expect(mockSpawn).not.toHaveBeenCalled();
  });

  test('runs Docker with run_eval_and_print.py when test set and model exist', async () => {
    const deps = {
      spawn: mockSpawn,
      fs: {
        existsSync: jest.fn((p) =>
          p.includes('test_white') || p.includes('test_black')
        ),
      },
      path,
    };

    const promise = runEvaluationAfterTraining(baseOpts, deps);

    expect(mockSpawn).toHaveBeenCalledWith(
      'docker',
      expect.arrayContaining([
        'run',
        '--rm',
        '-v',
        '/tmp/maia:/maia-individual',
        '-v',
        '/tmp/session_123:/session',
        '-w',
        '/maia-individual',
        'chess-mimic-training-amd64',
        'conda',
        'run',
        '--no-capture-output',
        '-n',
        'transfer_chess',
        'python',
        '-u',
        '3-analysis/run_eval_and_print.py',
        expect.stringContaining('final_models'),
        '/session',
        'testplayer',
      ]),
      expect.objectContaining({ cwd: '/tmp/chesster' })
    );

    expect(baseOpts.send).toHaveBeenCalledWith(
      'train',
      'Running evaluation on test set...',
      0.98,
      'status'
    );

    const closeCb = mockProcess.on.mock.calls.find((c) => c[0] === 'close')[1];
    closeCb(0);
    await promise;
  });

  test('pipes evaluation stdout to console.log and send()', async () => {
    const deps = {
      spawn: mockSpawn,
      fs: {
        existsSync: jest.fn((p) =>
          p.includes('test_white') || p.includes('test_black')
        ),
      },
      path,
    };

    const promise = runEvaluationAfterTraining(baseOpts, deps);

    const stdoutCb = mockProcess.stdout.on.mock.calls.find(
      (c) => c[0] === 'data'
    )[1];
    stdoutCb(Buffer.from('Test accuracy (white): 42.50% (n=100)\n'));
    stdoutCb(Buffer.from('Overall test accuracy: 42.50% (n=100)\n'));

    const closeCb = mockProcess.on.mock.calls.find((c) => c[0] === 'close')[1];
    closeCb(0);
    await promise;

    expect(consoleLogSpy).toHaveBeenCalledWith('Test accuracy (white): 42.50% (n=100)');
    expect(consoleLogSpy).toHaveBeenCalledWith('Overall test accuracy: 42.50% (n=100)');

    expect(baseOpts.send).toHaveBeenCalledWith(
      'train',
      'Test accuracy (white): 42.50% (n=100)',
      0.99,
      'log'
    );
    expect(baseOpts.send).toHaveBeenCalledWith(
      'train',
      'Overall test accuracy: 42.50% (n=100)',
      0.99,
      'log'
    );
  });

  test('handles evaluation failure and sends skip message', async () => {
    const deps = {
      spawn: mockSpawn,
      fs: {
        existsSync: jest.fn((p) =>
          p.includes('test_white') || p.includes('test_black')
        ),
      },
      path,
    };

    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    const promise = runEvaluationAfterTraining(baseOpts, deps);

    const closeCb = mockProcess.on.mock.calls.find((c) => c[0] === 'close')[1];
    closeCb(1);
    await promise;

    expect(consoleWarnSpy).toHaveBeenCalled();
    expect(baseOpts.send).toHaveBeenCalledWith(
      'train',
      expect.stringContaining('Evaluation skipped'),
      0.99,
      'status'
    );

    consoleWarnSpy.mockRestore();
  });
});
