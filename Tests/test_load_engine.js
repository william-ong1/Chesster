import path from 'path';
import { fileURLToPath } from 'url';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as engine from '../app/engine.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BIN_DIR = path.join(__dirname, '..', 'bin');

describe('loadEngine', () => {
  let fakeSpawn;

  beforeEach(() => {
    fakeSpawn = vi.fn();
  });

  afterEach(async () => {
    engine.unloadEngine();
  });

  it('throws when getBinPath returns null (lc0 not found)', async () => {
    const deps = {
      getBinPath: () => null,
      BIN_DIR,
      spawn: fakeSpawn,
    };
    await expect(engine.loadEngine('/some/weights.pb.gz', deps)).rejects.toThrow(
      'lc0 binary not found.'
    );
    expect(fakeSpawn).not.toHaveBeenCalled();
  });

  it('spawns lc0 with correct args when getBinPath returns a path', async () => {
    const lc0Path = '/fake/bin/lc0';
    const weightsPath = '/models/maia-1200.pb.gz';
    let stdoutCb;

    fakeSpawn.mockImplementation((cmd, args, opts) => {
      expect(cmd).toBe(lc0Path);
      expect(args).toEqual(['-w', weightsPath]);
      return {
        stdin: { write: vi.fn() },
        stdout: {
          on(ev, fn) {
            if (ev === 'data') stdoutCb = fn;
          },
        },
        stderr: { on: vi.fn() },
        on: vi.fn(),
        kill: vi.fn(),
      };
    });

    const deps = {
      getBinPath: () => lc0Path,
      BIN_DIR,
      spawn: fakeSpawn,
    };

    const loadPromise = engine.loadEngine(weightsPath, deps);

    // Simulate UCI handshake: uciok then readyok
    setImmediate(() => stdoutCb('uciok\n'));
    await new Promise(r => setImmediate(r));
    setImmediate(() => stdoutCb('readyok\n'));

    await loadPromise;

    expect(fakeSpawn).toHaveBeenCalledWith(lc0Path, ['-w', weightsPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    expect(engine.isEngineReady()).toBe(true);
  });

  it(
    'rejects on timeout waiting for uciok',
    async () => {
      const lc0Path = '/fake/bin/lc0';
      fakeSpawn.mockImplementation(() => ({
        stdin: { write: vi.fn() },
        stdout: { on: vi.fn() },
        stderr: { on: vi.fn() },
        on: vi.fn(),
        kill: vi.fn(),
      }));

      const deps = {
        getBinPath: () => lc0Path,
        BIN_DIR,
        spawn: fakeSpawn,
      };

      const loadPromise = engine.loadEngine('/w.pb.gz', deps);

      await expect(loadPromise).rejects.toThrow(/Engine timeout/);
    },
    12000
  );

  it('kills existing process before loading again', async () => {
    const lc0Path = '/fake/bin/lc0';
    const killFn = vi.fn();
    let stdoutCb;

    fakeSpawn.mockImplementation(() => ({
      stdin: { write: vi.fn() },
      stdout: {
        on(ev, fn) {
          if (ev === 'data') stdoutCb = fn;
        },
      },
      stderr: { on: vi.fn() },
      on: vi.fn(),
      kill: killFn,
    }));

    const deps = {
      getBinPath: () => lc0Path,
      BIN_DIR,
      spawn: fakeSpawn,
    };

    const load1 = engine.loadEngine('/w1.pb.gz', deps);
    setImmediate(() => stdoutCb('uciok\n'));
    await new Promise(r => setImmediate(r));
    setImmediate(() => stdoutCb('readyok\n'));
    await load1;

    expect(fakeSpawn).toHaveBeenCalledTimes(1);

    const load2 = engine.loadEngine('/w2.pb.gz', deps);
    expect(killFn).toHaveBeenCalled();
    setImmediate(() => stdoutCb('uciok\n'));
    await new Promise(r => setImmediate(r));
    setImmediate(() => stdoutCb('readyok\n'));
    await load2;

    expect(fakeSpawn).toHaveBeenCalledTimes(2);
  });
});
