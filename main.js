'use strict';

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path   = require('path');
const fs     = require('fs');
const { spawn, execSync } = require('child_process');

// ─── Paths ────────────────────────────────────────────────────────────────────

const ROOT     = __dirname;
const BIN_DIR  = path.join(ROOT, 'bin');
const MAIA_DIR = path.join(ROOT, 'maia-individual');
const MODELS_DIR = path.join(ROOT, 'models');
const INDIVIDUAL_MODELS_DIR = path.join(MODELS_DIR, 'individual');
const DATA_DIR = path.join(ROOT, 'data', 'processed');
const SCRIPTS_DIR = path.join(ROOT, 'scripts');

const MAIA_ELOS = [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900];

const SETUP_FLAG = path.join(ROOT, '.setup_complete');

// Detect platform and use appropriate Docker image
const PLATFORM = process.platform === 'darwin' && process.arch === 'arm64' 
  ? 'arm64' 
  : 'amd64';
const IMAGE_NAME = `chess-mimic-training-${PLATFORM}`;
const IMAGE_FLAG = path.join(ROOT, `.docker_image_built_${PLATFORM}`);

function dockerAvailable() {
  try {
    execSync('docker info', { stdio: 'ignore' });
    return true;
  } catch (_) {
    return false;
  }
}

// ─── Setup progress helper ────────────────────────────────────────────────────
// Sends both a human-readable message and a 0–100 percent for the progress bar.
// type: 'status' (shown in the status line) | 'log' (shown in terminal only)

function sendSetupProgress(win, message, percent = null, type = 'status') {
  win.webContents.send('setup:progress', { message, percent, type });
}

async function runFirstTimeSetup(win) {
  if (fs.existsSync(SETUP_FLAG)) {
    win.webContents.send('setup:done');
    return;
  }

  // Check Docker first (quick)
  sendSetupProgress(win, 'Checking Docker...', 5);
  if (!dockerAvailable()) {
    if (process.platform === 'linux') {
      sendSetupProgress(win, 'Docker not found. Installing Docker Engine...', 10);
      await new Promise((resolve, reject) => {
        const proc = spawn('bash', ['-c', 'curl -fsSL https://get.docker.com | sh'], {
          stdio: ['ignore', 'pipe', 'pipe']
        });
        proc.stdout.on('data', d =>
          sendSetupProgress(win, d.toString().trim(), null, 'log'));
        proc.stderr.on('data', d =>
          sendSetupProgress(win, d.toString().trim(), null, 'log'));
        proc.on('close', code => {
          if (code === 0) resolve();
          else reject(new Error('Docker installation failed.'));
        });
      }).catch(err => {
        win.webContents.send('setup:error', err.message);
        return;
      });
      sendSetupProgress(win, 'Docker installed successfully.', 30);
    } else {
      // Mac or Windows — can't auto-install, direct user to download
      win.webContents.send('setup:docker-needed');
      return;
    }
  }
  sendSetupProgress(win, 'Docker found.', 40);

  // Backend install is not needed - it's installed in Docker during image build
  // Trigger OpenCL tuning so first move isn't slow
  sendSetupProgress(win, 'Calibrating chess engine (one-time, ~1-2 minutes)...', 50);

  const lc0Path = getBinPath('lc0');
  const firstModel = fs.existsSync(MODELS_DIR)
    ? fs.readdirSync(MODELS_DIR).find(f => /^maia-\d+\.pb\.gz$/.test(f))
    : null;

  if (!lc0Path || !firstModel) {
    // No lc0 or no model yet — skip tuning, finish setup
    sendSetupProgress(win, 'Setup complete! Add Maia models (.pb.gz files) to models/ folder.', 100);
    fs.writeFileSync(SETUP_FLAG, 'done');
    win.webContents.send('setup:done');
    return;
  }

  return new Promise((resolve) => {
    const tuneProc = spawn(lc0Path, ['-w', path.join(MODELS_DIR, firstModel)], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    tuneProc.stdin.write('uci\n');

    const tuneTimeout = setTimeout(() => {
      tuneProc.kill();
      sendSetupProgress(win, 'Engine calibration timed out — continuing anyway.', 100);
      fs.writeFileSync(SETUP_FLAG, 'done');
      win.webContents.send('setup:done');
      resolve();
    }, 3 * 60 * 1000);

    tuneProc.stderr.on('data', d => {
      sendSetupProgress(win, d.toString().trim(), null, 'log');
    });

    tuneProc.stdout.on('data', d => {
      const txt = d.toString();
      sendSetupProgress(win, txt.trim(), null, 'log');
      if (txt.includes('uciok')) {
        clearTimeout(tuneTimeout);
        tuneProc.stdin.write('quit\n');
        sendSetupProgress(win, 'Engine ready.', 100);
        fs.writeFileSync(SETUP_FLAG, 'done');
        win.webContents.send('setup:done');
        resolve();
      }
    });

    tuneProc.on('close', () => {
      clearTimeout(tuneTimeout);
      fs.writeFileSync(SETUP_FLAG, 'done');
      win.webContents.send('setup:done');
      resolve();
    });
  });
}

/*function closestMaiaModel(elo) {
  const n = parseInt(elo, 10);
  const closest = MAIA_ELOS.reduce((a, b) =>
    Math.abs(b - n) < Math.abs(a - n) ? b : a
  );
  return {
    elo: closest,
    filename: `maia-${closest}.pb.gz`,
    path: path.join(MODELS_DIR, `maia-${closest}.pb.gz`)
  };
}*/

function closestMaiaModel(elo) {
  return {
    elo: 1900,
    filename: `maia-1900.pb.gz`,
    path: path.join(MODELS_DIR, `maia-1900.pb.gz`)
  };
}

function getBinPath(name) {
  const local = path.join(BIN_DIR, name);
  if (fs.existsSync(local)) return local;
  try {
    return execSync(`which ${name}`, { encoding: 'utf-8' }).trim();
  } catch (_) { return null; }
}

function getPythonBin() {
  for (const py of ['python3', 'python']) {
    try { execSync(`which ${py}`, { encoding: 'utf-8' }); return py; } catch (_) {}
  }
  return 'python3';
}

function envWithBin() {
  return { ...process.env, PATH: `${BIN_DIR}:${process.env.PATH}` };
}

// ─── First-run setup ──────────────────────────────────────────────────────────

function firstRunSetup() {
  [INDIVIDUAL_MODELS_DIR, DATA_DIR].forEach(d => {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
  });
  if (fs.existsSync(BIN_DIR)) {
    fs.readdirSync(BIN_DIR).forEach(f => {
      try { fs.chmodSync(path.join(BIN_DIR, f), 0o755); } catch (_) {}
    });
  }
}

// ─── System check ─────────────────────────────────────────────────────────────

function checkSystem() {
  const results = {};
  for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
    const p = getBinPath(bin);
    results[bin] = { ok: !!p, path: p || 'not found' };
  }
  const py = getPythonBin();
  try {
    const v = execSync(`${py} --version`, { encoding: 'utf-8' }).trim();
    results.python3 = { ok: true, path: v };
  } catch (_) {
    results.python3 = { ok: false, path: 'not found' };
  }
  results.maiaIndividual = {
    ok: fs.existsSync(path.join(MAIA_DIR, '1-data_generation', '9-pgn_to_training_data.sh')),
    path: MAIA_DIR
  };
  const models = fs.existsSync(MODELS_DIR)
    ? fs.readdirSync(MODELS_DIR).filter(f => /^maia-\d+\.pb\.gz$/.test(f))
    : [];
  results.baseModels = { ok: models.length > 0, path: models.join(', ') || 'none found' };
  return results;
}

function buildDockerImage(win) {
  return new Promise((resolve, reject) => {
    if (fs.existsSync(IMAGE_FLAG)) { resolve(); return; }

    win.webContents.send('setup:progress',
      { message: `Building Docker training image for ${PLATFORM} — 10-20 minutes on first run...`, percent: null, type: 'status' });

    const dockerfileArg = PLATFORM === 'arm64' 
      ? ['-f', 'Dockerfile.arm64']
      : ['-f', 'Dockerfile.amd64'];

    const proc = spawn('docker', [
      'build',
      ...dockerfileArg,
      '-t', IMAGE_NAME,
      '--progress=plain',
      '.'
    ], { cwd: ROOT });

    proc.stdout.on('data', d => {
      d.toString().split('\n').filter(l => l.trim())
        .forEach(l => win.webContents.send('setup:progress', { message: l, percent: null, type: 'log' }));
    });
    proc.stderr.on('data', d => {
      d.toString().split('\n').filter(l => l.trim())
        .forEach(l => win.webContents.send('setup:progress', { message: l, percent: null, type: 'log' }));
    });

    proc.on('close', code => {
      if (code === 0) {
        fs.writeFileSync(IMAGE_FLAG, 'done');
        resolve();
      } else {
        reject(new Error('Docker image build failed.'));
      }
    });
  });
}

// ─── Training pipeline ────────────────────────────────────────────────────────
//
// Progress bar breakdown across 4 steps:
//   clean  →  0 – 15 %
//   data   → 15 – 55 %
//   config → 55 – 65 %
//   train  → 65 – 98 %
//   done   → 100 %
//
// Each `training:progress` payload: { step, message, percent, type }
//   step    – 'clean' | 'data' | 'config' | 'train' | 'done'
//   message – human-readable log line
//   percent – 0-100 overall progress (null = no update to bar)
//   type    – 'status' (update headline) | 'log' (terminal-only line)

const STEP_RANGES = {
  clean:  [0,  15],
  data:   [15, 55],
  config: [55, 65],
  train:  [65, 98],
  done:   [100, 100],
};

function runTrainingPipeline(event, { pgnPath, username, userElo }) {
  return new Promise(async (resolve, reject) => {
    // interpolate within a step's range (frac 0.0–1.0)
    const stepPercent = (step, frac = 0) => {
      const [lo, hi] = STEP_RANGES[step] || [0, 0];
      return Math.round(lo + (hi - lo) * Math.min(1, Math.max(0, frac)));
    };

    const send = (step, message, frac = null, type = 'log') => {
      const percent = frac !== null ? stepPercent(step, frac) : null;
      event.sender.send('training:progress', { step, message, percent, type });
    };

    // status line + progress bar update
    const status = (step, message, frac = 0) => send(step, message, frac, 'status');

    const model      = closestMaiaModel(userElo);
    const sessionId  = Date.now();
    const outputDir  = path.join(DATA_DIR, `session_${sessionId}`);
    const cleanedPgn = path.join(outputDir, 'cleaned.pgn');
    const configPath = path.join(outputDir, 'config.yaml');
    const py         = getPythonBin();

    fs.mkdirSync(outputDir, { recursive: true });

    if (!fs.existsSync(IMAGE_FLAG)) {
      status('train', 'Building Docker image for the first time — this takes 10-20 minutes...', 0);
      try {
        await buildDockerImage({ webContents: { send: (_, payload) => {
          const msg = typeof payload === 'string' ? payload : payload.message;
          send('train', msg, null, typeof payload === 'object' ? payload.type : 'log');
        }}});
      } catch (err) {
        return reject(new Error('Docker image build failed: ' + err.message));
      }
    }

    if (!fs.existsSync(model.path)) {
      return reject(new Error(
        `Base model not found: ${model.filename}\nPlease place it in the models/ folder.`
      ));
    }

    // ── Step 1: Clean PGN ──────────────────────────────────────────────────
    status('clean', `Cleaning PGN for maia-individual compatibility...`, 0);

    const step1 = spawn(py, [
      path.join(SCRIPTS_DIR, 'clean_pgn.py'),
      pgnPath,
      cleanedPgn
    ]);

    let step1Out = '';
    step1.stdout.on('data', d => { step1Out += d.toString(); });
    step1.stderr.on('data', d => send('clean', d.toString().trim(), 0.5));

    step1.on('close', code => {
      if (code !== 0) return reject(new Error(`PGN cleaning failed.`));
      status('clean', step1Out.trim() || 'PGN cleaned successfully.', 1);

      // ── Step 2: Generate training data ──────────────────────────────────
      status('data', `Extracting games for "${username}" using Maia ${model.elo}...`, 0);

      const step2 = spawn('docker', [
        'run', '--rm',
        '-v', `${MAIA_DIR}:/maia-individual`,
        '-v', `${outputDir}:/session`,
        '-w', '/maia-individual/1-data_generation',
        IMAGE_NAME,
        'conda', 'run', '-n', 'transfer_chess',
        'bash', '9-pgn_to_training_data.sh',
        '/session/cleaned.pgn', '/session', username
      ]);

      // Try to loosely estimate data-generation progress from line count
      let dataLines = 0;
      const DATA_LINES_EST = 200; // rough expected output lines

      step2.stdout.on('data', d => {
        dataLines += d.toString().split('\n').filter(l => l.trim()).length;
        d.toString().split('\n').filter(l => l.trim()).forEach(l =>
          send('data', l, Math.min(0.95, dataLines / DATA_LINES_EST)));
      });
      step2.stderr.on('data', d => {
        dataLines += d.toString().split('\n').filter(l => l.trim()).length;
        d.toString().split('\n').filter(l => l.trim()).forEach(l =>
          send('data', l, Math.min(0.95, dataLines / DATA_LINES_EST)));
      });

      step2.on('close', code2 => {
        if (code2 !== 0) return reject(new Error('Training data generation failed.'));
        status('data', 'Training data generated successfully.', 1);

        // ── Step 3: Build config ───────────────────────────────────────────
        status('config', 'Building training config...', 0);

        const templatePath = path.join(MAIA_DIR, '2-training', 'final_config.yaml');
        if (!fs.existsSync(templatePath)) {
          return reject(new Error('final_config.yaml not found in maia-individual/2-training/'));
        }

        let config = fs.readFileSync(templatePath, 'utf-8');
        config = config.replace(/gpu:\s*\d+/, '');
        config = config.replace(
          /path:\s*['"]path to player data['"]/,
          `path: '/session'`
        );
        config = config.replace(
          /path:\s*["']maia-\d+["']/,
          `path: "maia-${model.elo}"`
        );
        config = config.replace(
          /#name:\s*['"]+/,
          `name: '${username}'`
        );

        fs.writeFileSync(configPath, config);
        status('config', `Config written. Using base model: maia-${model.elo}`, 1);

        // ── Step 4: Run training ───────────────────────────────────────────
        status('train', 'Starting neural network training. This may take a while...', 0);

        const step3 = spawn('docker', [
          'run', '--rm',
          '-e', 'PYTHONUNBUFFERED=1',
          '-v', `${MAIA_DIR}:/maia-individual`,
          '-v', `${outputDir}:/session`,
          //'-v', `${MODELS_DIR}:/models`,
          '-w', '/maia-individual',
          IMAGE_NAME,
          'conda', 'run', '--no-capture-output', '-n', 'transfer_chess',
          'python', '-u', '2-training/train_transfer.py', '/session/config.yaml'
        ]);

        // Parse epoch/step info from training output to drive the progress bar
        // Looks for patterns like "Epoch 3/20" or "step 45/200"
        let trainFrac = 0;

        const parseTrainFrac = (line) => {
          // "Epoch X/Y" style
          let m = line.match(/[Ee]poch\s+(\d+)\s*\/\s*(\d+)/);
          if (m) return Math.min(0.97, parseInt(m[1]) / parseInt(m[2]));
          // "step X/Y" style
          m = line.match(/[Ss]tep\s+(\d+)\s*\/\s*(\d+)/);
          if (m) return Math.min(0.97, parseInt(m[1]) / parseInt(m[2]));
          return null;
        };

        step3.stdout.on('data', d => {
          d.toString().split('\n').filter(l => l.trim()).forEach(l => {
            const f = parseTrainFrac(l);
            if (f !== null) trainFrac = f;
            send('train', l, trainFrac);
          });
        });
        step3.stderr.on('data', d => {
          d.toString().split('\n').filter(l => l.trim()).forEach(l => {
            const f = parseTrainFrac(l);
            if (f !== null) trainFrac = f;
            send('train', l, trainFrac);
          });
        });

        step3.on('close', code3 => {
          if (code3 !== 0) return reject(new Error('Training script failed.'));

          // Find output model in final_models/
          const finalModelsDir = path.join(MAIA_DIR, 'final_models');
          let outputModel = null;
          if (fs.existsSync(finalModelsDir)) {
            const files = fs.readdirSync(finalModelsDir)
              .filter(f => f.endsWith('.pb.gz'))
              .map(f => ({ f, t: fs.statSync(path.join(finalModelsDir, f)).mtimeMs }))
              .sort((a, b) => b.t - a.t);
            if (files.length > 0) {
              const src = path.join(finalModelsDir, files[0].f);
              outputModel = path.join(INDIVIDUAL_MODELS_DIR, `${username}_${sessionId}.pb.gz`);
              fs.copyFileSync(src, outputModel);
            }
          }

          event.sender.send('training:progress', {
            step: 'done',
            message: `Training complete!${outputModel ? ` Model saved to models/individual/` : ''}`,
            percent: 100,
            type: 'status'
          });
          resolve({ outputModel });
        });
      });
    });
  });
}

// ─── Chess engine (UCI) ───────────────────────────────────────────────────────

let engineProc = null;
let engineReady = false;
let engineBuffer = '';
let engineQueue = [];
let engineStderr = '';

function engineSend(cmd) {
  if (engineProc) engineProc.stdin.write(cmd + '\n');
}

function engineReadUntil(pred, timeout = 10000) {
  return new Promise((res, rej) => {
    const t = setTimeout(() => {
      rej(new Error(
        `Engine timeout after ${timeout}ms.\n` +
        `lc0 stderr: ${engineStderr.slice(-500) || '(empty)'}\n` +
        `Make sure lc0 v0.23.x is in bin/ and the weights file is a valid .pb.gz`
      ));
    }, timeout);
    const push = () => {
      engineQueue.push(line => {
        if (pred(line)) { clearTimeout(t); res(line); } else push();
      });
    };
    push();
  });
}

async function loadEngine(weightsPath) {
  if (engineProc) { engineProc.kill(); engineProc = null; engineReady = false; }

  const lc0 = getBinPath('lc0');
  if (!lc0) throw new Error('lc0 binary not found.');

  engineBuffer = '';
  engineQueue  = [];

  engineProc = spawn(lc0, ['-w', weightsPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

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
    console.error('[lc0 stderr]', d.toString().trim());
  }); 
  engineProc.on('close', () => { engineProc = null; engineReady = false; });

  engineSend('uci');
  await engineReadUntil(l => l === 'uciok', 10000);
  engineSend('setoption name Nodes value 1');
  engineSend('isready');
  await engineReadUntil(l => l === 'readyok', 5000);
  engineReady = true;
}

async function getEngineMove(fen) {
  if (!engineReady) throw new Error('Engine not loaded.');
  engineSend(`position fen ${fen}`);
  engineSend('go nodes 1');
  const line = await engineReadUntil(l => l.startsWith('bestmove'), 8000);
  return line.split(' ')[1];
}

// ─── IPC Handlers ─────────────────────────────────────────────────────────────

function registerHandlers() {
  ipcMain.handle('system:check', async () => checkSystem());

  ipcMain.handle('dialog:open-pgn', async () => {
    const r = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: [{ name: 'PGN Files', extensions: ['pgn'] }]
    });
    return r.canceled ? null : r.filePaths[0];
  });

  ipcMain.handle('models:list', async () => {
    let lst = [];
    let lst2 = [];
    if (fs.existsSync(INDIVIDUAL_MODELS_DIR)){
      lst = fs.readdirSync(INDIVIDUAL_MODELS_DIR)
        .filter(f => f.endsWith('.pb.gz'))
        .map(f => ({
          name: f,
          path: path.join(INDIVIDUAL_MODELS_DIR, f),
          mtime: fs.statSync(path.join(INDIVIDUAL_MODELS_DIR, f)).mtime
        }))
        .sort((a, b) => b.mtime - a.mtime);
    }
    lst2 = fs.readdirSync(MODELS_DIR)
      .filter(f => f.endsWith('.pb.gz'))
      .map(f => ({
        name: f,
        path: path.join(MODELS_DIR, f),
        mtime: fs.statSync(path.join(MODELS_DIR, f)).mtime
      }))
      .sort((a, b) => b.mtime - a.mtime);
    lst.push(...lst2);
    return lst;
  });

  ipcMain.handle('models:check', async (_, { elo }) => {
    const m = closestMaiaModel(elo);
    return { ...m, exists: fs.existsSync(m.path) };
  });

  ipcMain.handle('training:start', async (event, { pgnPath, username, userElo }) => {
    runTrainingPipeline(event, { pgnPath, username, userElo })
      .catch(err => event.sender.send('training:error', { message: err.message }));
    return { ok: true };
  });

  ipcMain.handle('engine:load', async (_, { weightsPath }) => {
    try {
      engineStderr = '';
      await loadEngine(weightsPath);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  });

  ipcMain.handle('engine:move', async (_, { fen }) => {
    try {
      return { move: await getEngineMove(fen) };
    } catch (err) {
      return { error: err.message };
    }
  });

  ipcMain.handle('engine:unload', async () => {
    if (engineProc) { engineProc.kill(); engineProc = null; engineReady = false; }
    return { ok: true };
  });

  ipcMain.handle('shell:open', async (_, { url }) => {
    await shell.openExternal(url);
  });
}

// ─── Window ───────────────────────────────────────────────────────────────────

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 1000,
    minHeight: 700,
    backgroundColor: '#0a0008',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'app', 'preload.js')
    }
  });
  win.loadFile(path.join(__dirname, 'app', 'index.html'));
  win.webContents.on('did-finish-load', () => {
    runFirstTimeSetup(win).catch(console.error);
  });
  return win;
}

app.whenReady().then(() => {
  firstRunSetup();
  registerHandlers();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (engineProc) engineProc.kill();
  if (process.platform !== 'darwin') app.quit();
});