'use strict';

/** Engine state and loadEngine logic for testability. */

let engineProc = null;
let engineReady = false;
let engineBuffer = '';
let engineQueue = [];
let engineStderr = '';

function engineSend(proc, cmd) {
  if (proc && proc.stdin) proc.stdin.write(cmd + '\n');
}

function engineReadUntil(pred, timeout, queue, stderrRef) {
  return new Promise((res, rej) => {
    const t = setTimeout(() => {
      rej(new Error(
        `Engine timeout after ${timeout}ms.\n` +
        `lc0 stderr: ${(stderrRef.current || '').slice(-500) || '(empty)'}\n` +
        `Make sure lc0 v0.23.x is in bin/ and the weights file is a valid .pb.gz`
      ));
    }, timeout);
    const push = () => {
      queue.push(line => {
        if (pred(line)) { clearTimeout(t); res(line); } else push(); }
      );
    };
    push();
  });
}

/**
 * Load the UCI engine (lc0) with the given weights.
 * @param {string} weightsPath - Path to .pb.gz weights file
 * @param {{ getBinPath: (name: string, binDir: string) => string|null, BIN_DIR: string, spawn: typeof import('child_process').spawn }} deps
 */
async function loadEngine(weightsPath, deps) {
  const { getBinPath, BIN_DIR, spawn } = deps;

  if (engineProc) { engineProc.kill(); engineProc = null; engineReady = false; }

  const lc0 = getBinPath('lc0', BIN_DIR);
  if (!lc0) throw new Error('lc0 binary not found.');

  engineBuffer = '';
  engineQueue = [];
  engineStderr = '';

  engineProc = spawn(lc0, ['-w', weightsPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  const stderrRef = { current: '' };

  engineProc.stdout.on('data', chunk => {
    engineBuffer += chunk.toString();
    const lines = engineBuffer.split('\n');
    engineBuffer = lines.pop();
    for (const line of lines) {
      const t = line.trim();
      if (t && engineQueue.length) engineQueue.shift()(t);
    }
  });

  engineProc.stderr.on('data', d => {
    engineStderr += d.toString();
    stderrRef.current = engineStderr;
  });
  engineProc.on('close', () => { engineProc = null; engineReady = false; });

  engineSend(engineProc, 'uci');
  await engineReadUntil(l => l === 'uciok', 10000, engineQueue, stderrRef);
  engineSend(engineProc, 'setoption name Nodes value 1');
  engineSend(engineProc, 'isready');
  await engineReadUntil(l => l === 'readyok', 5000, engineQueue, stderrRef);
  engineReady = true;
}

async function getEngineMove(fen) {
  if (!engineReady) throw new Error('Engine not loaded.');
  engineSend(engineProc, `position fen ${fen}`);
  engineSend(engineProc, 'go nodes 1');
  const stderrRef = { current: engineStderr };
  const line = await engineReadUntil(l => l.startsWith('bestmove'), 8000, engineQueue, stderrRef);
  return line.split(' ')[1];
}

function getEngineStderr() {
  return engineStderr;
}

function resetEngineStderr() {
  engineStderr = '';
}

function getEngineProc() {
  return engineProc;
}

function isEngineReady() {
  return engineReady;
}

function unloadEngine() {
  if (engineProc) { engineProc.kill(); engineProc = null; engineReady = false; }
}

module.exports = {
  loadEngine,
  getEngineMove,
  getEngineStderr,
  resetEngineStderr,
  getEngineProc,
  isEngineReady,
  unloadEngine,
};
