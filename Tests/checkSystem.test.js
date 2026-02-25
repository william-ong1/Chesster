const path = require('path');
const fs = require('fs');
const os = require('os');
const { checkSystem } = require('../app/functions');

// Isolated temp directory tree so tests don't depend on the real project layout
function makeTempDirs() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'checksys-'));
  const BIN_DIR = path.join(root, 'bin');
  const MAIA_DIR = path.join(root, 'maia-individual');
  const MODELS_DIR = path.join(root, 'models');
  const dataGenDir = path.join(MAIA_DIR, '1-data_generation');

  fs.mkdirSync(BIN_DIR, {recursive: true});
  fs.mkdirSync(dataGenDir, {recursive: true});
  fs.mkdirSync(MODELS_DIR, {recursive: true});

  return {root, BIN_DIR, MAIA_DIR, MODELS_DIR, dataGenDir};
}

function cleanup(root) {
  fs.rmSync(root, {recursive: true, force: true});
}

describe('checkSystem', () => {
  let dirs;

  beforeEach(() => {
    dirs = makeTempDirs();
  });

  afterEach(() => {
    cleanup(dirs.root);
  });

  // With an empty bin/ directory, none of the three binaries should be found
  // locally (they may still be found on $PATH depending on the system)
  test('reports binaries as not found when bin/ is empty', () => {
    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
      expect(res[bin]).toBeDefined();
      expect(typeof res[bin].ok).toBe('boolean');
      expect(typeof res[bin].path).toBe('string');
    }
  });

  // Place dummy files in bin/ so getBinPath finds them locally
  test('reports binaries as ok when present in bin/', () => {
    for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
      fs.writeFileSync(path.join(dirs.BIN_DIR, bin), '');
    }

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
      expect(res[bin].ok).toBe(true);
      expect(res[bin].path).toBe(path.join(dirs.BIN_DIR, bin));
    }
  });

  // Python should always be detected (the test runner itself is running on
  // a system with Python), so we just verify the shape of the result
  test('detects python and returns version string', () => {
    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.python3).toBeDefined();
    expect(typeof res.python3.ok).toBe('boolean');
    expect(typeof res.python3.path).toBe('string');
  });

  // The maia-individual check looks for a specific shell script
  test('reports maiaIndividual as not ok when script is missing', () => {
    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.maiaIndividual.ok).toBe(false);
    expect(res.maiaIndividual.path).toBe(dirs.MAIA_DIR);
  });

  // Create the expected script so the check passes
  test('reports maiaIndividual as ok when script exists', () => {
    fs.writeFileSync(
      path.join(dirs.dataGenDir, '9-pgn_to_training_data.sh'), ''
    );

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.maiaIndividual.ok).toBe(true);
  });

  // Empty models/ directory means no base models found
  test('reports baseModels as not ok when models/ is empty', () => {
    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.baseModels.ok).toBe(false);
    expect(res.baseModels.path).toBe('none found');
  });

  // Place maia weight files so the check detects them
  test('reports baseModels as ok when maia .pb.gz files exist', () => {
    fs.writeFileSync(path.join(dirs.MODELS_DIR, 'maia-1100.pb.gz'), '');
    fs.writeFileSync(path.join(dirs.MODELS_DIR, 'maia-1500.pb.gz'), '');

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.baseModels.ok).toBe(true);
    expect(res.baseModels.path).toContain('maia-1100.pb.gz');
    expect(res.baseModels.path).toContain('maia-1500.pb.gz');
  });

  // Non-maia files in models/ should be ignored by the regex filter
  test('ignores non-maia files in models/', () => {
    fs.writeFileSync(path.join(dirs.MODELS_DIR, 'random-net.pb.gz'), '');
    fs.writeFileSync(path.join(dirs.MODELS_DIR, 'weights.onnx'), '');

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.baseModels.ok).toBe(false);
    expect(res.baseModels.path).toBe('none found');
  });

  // If models/ doesn't exist at all, baseModels should still report gracefully
  test('handles missing models/ directory', () => {
    fs.rmSync(dirs.MODELS_DIR, {recursive: true});

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.baseModels.ok).toBe(false);
    expect(res.baseModels.path).toBe('none found');
  });

  // Full happy path: everything present
  test('all checks pass when everything is set up', () => {
    for (const bin of ['lc0', 'pgn-extract', 'trainingdata-tool']) {
      fs.writeFileSync(path.join(dirs.BIN_DIR, bin), '');
    }
    fs.writeFileSync(
      path.join(dirs.dataGenDir, '9-pgn_to_training_data.sh'), ''
    );
    fs.writeFileSync(path.join(dirs.MODELS_DIR, 'maia-1500.pb.gz'), '');

    const res = checkSystem({
      BIN_DIR: dirs.BIN_DIR,
      MAIA_DIR: dirs.MAIA_DIR,
      MODELS_DIR: dirs.MODELS_DIR,
      ROOT: dirs.root,
    });

    expect(res.lc0.ok).toBe(true);
    expect(res['pgn-extract'].ok).toBe(true);
    expect(res['trainingdata-tool'].ok).toBe(true);
    expect(res.maiaIndividual.ok).toBe(true);
    expect(res.baseModels.ok).toBe(true);
  });
});