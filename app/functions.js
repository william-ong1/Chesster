'use strict';

const path = require('path');
const fs   = require('fs');
const { execSync } = require('child_process');

/** Supported Maia ELO brackets. */
const MAIA_ELOS  = [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900];

/** Docker image name used for GPU training containers. */
const IMAGE_NAME = 'chess-mimic-training';

/** Builds all project path constants from a given root directory. */
function makePaths(root) {
  const BIN_DIR              = path.join(root, 'bin');
  const MAIA_DIR             = path.join(root, 'maia-individual');
  const MODELS_DIR           = path.join(root, 'models');
  const INDIVIDUAL_MODELS_DIR = path.join(MODELS_DIR, 'individual');
  const DATA_DIR             = path.join(root, 'data', 'processed');
  const SCRIPTS_DIR          = path.join(root, 'scripts');
  const SETUP_FLAG           = path.join(root, '.setup_complete');
  const IMAGE_FLAG           = path.join(root, '.docker_image_built');

  return {
    ROOT: root, BIN_DIR, MAIA_DIR, MODELS_DIR,
    INDIVIDUAL_MODELS_DIR, DATA_DIR, SCRIPTS_DIR,
    SETUP_FLAG, IMAGE_FLAG,
  };
}

// ─── Pure helpers ─────────────────────────────────────────────────────────────

/** Finds the nearest supported Maia ELO and returns { elo, filename, path }. */
function closestMaiaModel(elo, modelsDir) {
  const n = parseInt(elo, 10);
  const closest = MAIA_ELOS.reduce((a, b) =>
    Math.abs(b - n) < Math.abs(a - n) ? b : a
  );
  return {
    elo: closest,
    filename: `maia-${closest}.pb.gz`,
    path: path.join(modelsDir, `maia-${closest}.pb.gz`),
  };
}

// ─── Filesystem / exec helpers ────────────────────────────────────────────────

/** Resolves a binary by name, checking binDir first then $PATH. */
function getBinPath(name, binDir) {
  const local = path.join(binDir, name);
  if (fs.existsSync(local)) return local;
  try {
    return execSync(`which ${name}`, { encoding: 'utf-8' }).trim();
  } catch (_) { return null; }
}

/** Finds the best available Python interpreter (prefers project .venv). */
function getPythonBin(root) {
  const venvPy  = path.join(root, '.venv', 'bin', 'python');
  const venvPy3 = path.join(root, '.venv', 'bin', 'python3');
  if (fs.existsSync(venvPy))  return venvPy;
  if (fs.existsSync(venvPy3)) return venvPy3;
  for (const py of ['python3', 'python']) {
    try { execSync(`which ${py}`, { encoding: 'utf-8' }); return py; } catch (_) {}
  }
  return 'python3';
}

/** Returns a copy of process.env with binDir prepended to PATH. */
function envWithBin(binDir) {
  return { ...process.env, PATH: `${binDir}:${process.env.PATH}` };
}

/** Checks whether Docker is installed and the daemon is running. */
function dockerAvailable() {
  try {
    execSync('docker info', { stdio: 'ignore' });
    return true;
  } catch (_) {
    return false;
  }
}

// ─── First-run directory bootstrap ────────────────────────────────────────────

/** Creates any missing directories from the given array (recursive). */
function ensureDirectories(dirs) {
  dirs.forEach(d => {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
  });
}

/** Sets executable permissions (755) on all files in binDir. */
function chmodBinaries(binDir) {
  if (fs.existsSync(binDir)) {
    fs.readdirSync(binDir).forEach(f => {
      try { fs.chmodSync(path.join(binDir, f), 0o755); } catch (_) {}
    });
  }
}

// ─── System check ─────────────────────────────────────────────────────────────

/** Aggregates the status of all required system dependencies into a result map. */
function checkSystem({ BIN_DIR, MAIA_DIR, MODELS_DIR, ROOT }) {
  const results = {};
  for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
    const p = getBinPath(bin, BIN_DIR);
    results[bin] = { ok: !!p, path: p || 'not found' };
  }
  const py = getPythonBin(ROOT);
  try {
    const v = execSync(`${py} --version`, { encoding: 'utf-8' }).trim();
    results.python3 = { ok: true, path: v };
  } catch (_) {
    results.python3 = { ok: false, path: 'not found' };
  }
  results.maiaIndividual = {
    ok: fs.existsSync(path.join(MAIA_DIR, '1-data_generation', '9-pgn_to_training_data.sh')),
    path: MAIA_DIR,
  };
  const models = fs.existsSync(MODELS_DIR)
    ? fs.readdirSync(MODELS_DIR).filter(f => /^maia-\d+\.pb\.gz$/.test(f))
    : [];
  results.baseModels = { ok: models.length > 0, path: models.join(', ') || 'none found' };
  return results;
}

// ─── Model listing ────────────────────────────────────────────────────────────

/** Lists all .pb.gz weight files from both individual and base model directories. */
function listModels(modelsDir, individualModelsDir) {
  let lst = [];
  if (fs.existsSync(individualModelsDir)) {
    lst = fs.readdirSync(individualModelsDir)
      .filter(f => f.endsWith('.pb.gz'))
      .map(f => ({
        name: f,
        path: path.join(individualModelsDir, f),
        mtime: fs.statSync(path.join(individualModelsDir, f)).mtime,
      }))
      .sort((a, b) => b.mtime - a.mtime);
  }
  const lst2 = fs.readdirSync(modelsDir)
    .filter(f => f.endsWith('.pb.gz'))
    .map(f => ({
      name: f,
      path: path.join(modelsDir, f),
      mtime: fs.statSync(path.join(modelsDir, f)).mtime,
    }))
    .sort((a, b) => b.mtime - a.mtime);
  lst.push(...lst2);
  return lst;
}

// ─── Training config builder ──────────────────────────────────────────────────

/** Reads a YAML config template and substitutes the data/model paths for training. */
function buildTrainingConfig(templatePath, modelFilename) {
  if (!fs.existsSync(templatePath)) {
    throw new Error('final_config.yaml not found in maia-individual/2-training/');
  }
  let config = fs.readFileSync(templatePath, 'utf-8');
  config = config.replace(
    /path:\s*['"]path to player data['"]/,
    `path: '/session'`
  );
  config = config.replace(
    /path:\s*["']maia-\d+["']/,
    `path: "/models/${modelFilename}"`
  );
  return config;
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  MAIA_ELOS,
  IMAGE_NAME,
  makePaths,
  closestMaiaModel,
  getBinPath,
  getPythonBin,
  envWithBin,
  dockerAvailable,
  ensureDirectories,
  chmodBinaries,
  checkSystem,
  listModels,
  buildTrainingConfig,
};
