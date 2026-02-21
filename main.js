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

const IMAGE_NAME = 'chess-mimic-training';
const IMAGE_FLAG = path.join(ROOT, '.docker_image_built');

function dockerAvailable() {
  try {
    execSync('docker info', { stdio: 'ignore' });
    return true;
  } catch (_) {
    return false;
  }
}

async function runFirstTimeSetup(win) {
  if (fs.existsSync(SETUP_FLAG)) {
    win.webContents.send('setup:done');
    return;
  }

  // Check Docker first (quick)
  win.webContents.send('setup:progress', 'Checking Docker...');
if (!dockerAvailable()) {
  if (process.platform === 'linux') {
    win.webContents.send('setup:progress', 'Docker not found. Installing Docker Engine...');
    await new Promise((resolve, reject) => {
      const proc = spawn('bash', ['-c', 'curl -fsSL https://get.docker.com | sh'], {
        stdio: ['ignore', 'pipe', 'pipe']
      });
      proc.stdout.on('data', d =>
        win.webContents.send('setup:progress', d.toString().trim()));
      proc.stderr.on('data', d =>
        win.webContents.send('setup:progress', d.toString().trim()));
      proc.on('close', code => {
        if (code === 0) resolve();
        else reject(new Error('Docker installation failed.'));
      });
    }).catch(err => {
      win.webContents.send('setup:error', err.message);
      return;
    });
    win.webContents.send('setup:progress', 'Docker installed successfully.');
  } else {
    // Mac or Windows — can't auto-install, direct user to download
    win.webContents.send('setup:docker-needed');
    return;
  }
}
win.webContents.send('setup:progress', 'Docker found.');

  win.webContents.send('setup:progress', 'Installing maia-individual backend...');
  const py = getPythonBin();
  win.webContents.send('setup:progress', `Using Python: ${py}`);
  win.webContents.send('setup:progress', `Working directory: ${MAIA_DIR}`);

  return new Promise((resolve, reject) => {
    const proc = spawn(py, ['setup.py', 'install'], {
      cwd: MAIA_DIR,
      env: envWithBin()
    });

    // Timeout after 3 minutes
    const timeout = setTimeout(() => {
      proc.kill();
      win.webContents.send('setup:error', 'setup.py install timed out after 3 minutes.');
      reject(new Error('timeout'));
    }, 3 * 60 * 1000);

    proc.stdout.on('data', d =>
      win.webContents.send('setup:progress', d.toString().trim()));
    proc.stderr.on('data', d =>
      win.webContents.send('setup:progress', d.toString().trim()));

proc.on('close', code => {
  clearTimeout(timeout);
  if (code !== 0) {
    win.webContents.send('setup:error', `setup.py install failed with exit code ${code}`);
    reject(new Error('setup.py install failed'));
    return;
  }

  // Trigger OpenCL tuning so first move isn't slow
  win.webContents.send('setup:progress', 'Calibrating chess engine (one-time, ~1-2 minutes)...');

  const lc0Path = getBinPath('lc0');
  const firstModel = fs.existsSync(MODELS_DIR)
    ? fs.readdirSync(MODELS_DIR).find(f => /^maia-\d+\.pb\.gz$/.test(f))
    : null;

  if (!lc0Path || !firstModel) {
    // No lc0 or no model yet — skip tuning, finish setup
    win.webContents.send('setup:progress', 'Skipping engine calibration (no model found in models/).');
    fs.writeFileSync(SETUP_FLAG, 'done');
    win.webContents.send('setup:done');
    resolve();
    return;
  }

  const tuneProc = spawn(lc0Path, ['-w', path.join(MODELS_DIR, firstModel)], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  tuneProc.stdin.write('uci\n');

  const tuneTimeout = setTimeout(() => {
    tuneProc.kill();
    win.webContents.send('setup:progress', 'Engine calibration timed out — continuing anyway.');
    fs.writeFileSync(SETUP_FLAG, 'done');
    win.webContents.send('setup:done');
    resolve();
  }, 3 * 60 * 1000);

  tuneProc.stderr.on('data', d => {
    win.webContents.send('setup:progress', d.toString().trim());
  });

  tuneProc.stdout.on('data', d => {
    const txt = d.toString();
    win.webContents.send('setup:progress', txt.trim());
    if (txt.includes('uciok')) {
      clearTimeout(tuneTimeout);
      tuneProc.stdin.write('quit\n');
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
  });
}

function closestMaiaModel(elo) {
  const n = parseInt(elo, 10);
  const closest = MAIA_ELOS.reduce((a, b) =>
    Math.abs(b - n) < Math.abs(a - n) ? b : a
  );
  return {
    elo: closest,
    filename: `maia-${closest}.pb.gz`,
    path: path.join(MODELS_DIR, `maia-${closest}.pb.gz`)
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
      'Building Docker training image — 10-20 minutes on first run...');

    const proc = spawn('docker', [
      'build', '-t', IMAGE_NAME, '--progress=plain', '.'
    ], { cwd: ROOT });

    proc.stdout.on('data', d => {
      d.toString().split('\n').filter(l => l.trim())
        .forEach(l => win.webContents.send('setup:progress', l));
    });
    proc.stderr.on('data', d => {
      d.toString().split('\n').filter(l => l.trim())
        .forEach(l => win.webContents.send('setup:progress', l));
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

function runTrainingPipeline(event, { pgnPath, username, userElo }) {
  return new Promise(async (resolve, reject) => {
    const send = (step, message) =>
      event.sender.send('training:progress', { step, message });

    const model      = closestMaiaModel(userElo);
    const sessionId  = Date.now();
    const outputDir  = path.join(DATA_DIR, `session_${sessionId}`);
    const cleanedPgn = path.join(outputDir, 'cleaned.pgn');
    const configPath = path.join(outputDir, 'config.yaml');
    const py         = getPythonBin();

    fs.mkdirSync(outputDir, { recursive: true });

    if (!fs.existsSync(IMAGE_FLAG)) {
  send('train', 'Building Docker image for the first time — this takes 10-20 minutes...');
  try {
    await buildDockerImage({ webContents: { send: (_, msg) => send('train', msg) } });
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
    send('clean', `Cleaning PGN for maia-individual compatibility...`);

    const step1 = spawn(py, [
      path.join(SCRIPTS_DIR, 'clean_pgn.py'),
      pgnPath,
      cleanedPgn
    ]);

    let step1Out = '';
    step1.stdout.on('data', d => { step1Out += d.toString(); });
    step1.stderr.on('data', d => send('clean', d.toString().trim()));

    step1.on('close', code => {
      if (code !== 0) return reject(new Error(`PGN cleaning failed.`));
      send('clean', step1Out.trim() || 'PGN cleaned successfully.');

      // ── Step 2: Generate training data ──────────────────────────────────
      send('data', `Extracting games for "${username}" using Maia ${model.elo}...`);

      const script = path.join(MAIA_DIR, '1-data_generation', '9-pgn_to_training_data.sh');
      const step2 = spawn('docker', [
  'run', '--rm', '--gpus', 'all',
  '-v', `${MAIA_DIR}:/maia-individual`,
  '-v', `${outputDir}:/session`,
  '-w', '/maia-individual/1-data_generation',
  IMAGE_NAME,
  'conda', 'run', '-n', 'transfer_chess',
  'bash', '9-pgn_to_training_data.sh',
  '/session/cleaned.pgn', '/session', username
]);

      step2.stdout.on('data', d => send('data', d.toString().trim()));
      step2.stderr.on('data', d => send('data', d.toString().trim()));

      step2.on('close', code2 => {
        if (code2 !== 0) return reject(new Error('Training data generation failed.'));
        send('data', 'Training data generated successfully.');

        // ── Step 3: Build config ───────────────────────────────────────────
        send('train', 'Building training config...');

        const templatePath = path.join(MAIA_DIR, '2-training', 'final_config.yaml');
        if (!fs.existsSync(templatePath)) {
          return reject(new Error('final_config.yaml not found in maia-individual/2-training/'));
        }

        let config = fs.readFileSync(templatePath, 'utf-8');
        config = config.replace(
  /path:\s*['"]path to player data['"]/,
  `path: '/session'`
);
config = config.replace(
  /path:\s*["']maia-\d+["']/,
  `path: "/models/${model.filename}"`
);

        fs.writeFileSync(configPath, config);
        send('train', `Config written. Using base model: maia-${model.elo}`);

        // ── Step 4: Run training ───────────────────────────────────────────
        send('train', 'Starting neural network training. This may take a while...');

        const step3 = spawn('docker', [
  'run', '--rm', '--gpus', 'all',
  '-v', `${MAIA_DIR}:/maia-individual`,
  '-v', `${outputDir}:/session`,
  '-v', `${MODELS_DIR}:/models`,        // ← add this
  '-w', '/maia-individual',
  IMAGE_NAME,
  'conda', 'run', '-n', 'transfer_chess',
  'python', '2-training/train_transfer.py', '/session/config.yaml'
]);

        step3.stdout.on('data', d => {
          const text = d.toString().trim();
          if (text) send('train', text);
        });
        step3.stderr.on('data', d => {
          const text = d.toString().trim();
          if (text) send('train', text);
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

          send('done', `Training complete!${outputModel ? ` Model saved to models/individual/` : ''}`);
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
    let lst2 = []
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