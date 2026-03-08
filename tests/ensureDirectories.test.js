const path = require('path');
const fs = require('fs');
const os = require('os');
const { ensureDirectories } = require('../app/functions');

function makeTempRoot() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'ensuredirs-'));
}

function cleanup(root) {
  fs.rmSync(root, { recursive: true, force: true });
}

describe('ensureDirectories', () => {
  let root;

  beforeEach(() => {
    root = makeTempRoot();
  });

  afterEach(() => {
    cleanup(root);
  });

  test('creates a single missing directory', () => {
    const dir = path.join(root, 'alpha');
    ensureDirectories([dir]);
    expect(fs.existsSync(dir)).toBe(true);
    expect(fs.statSync(dir).isDirectory()).toBe(true);
  });

  test('creates multiple missing directories', () => {
    const dirs = [
      path.join(root, 'one'),
      path.join(root, 'two'),
      path.join(root, 'three'),
    ];
    ensureDirectories(dirs);
    dirs.forEach(d => {
      expect(fs.existsSync(d)).toBe(true);
    });
  });

  test('creates nested directories recursively', () => {
    const deep = path.join(root, 'a', 'b', 'c');
    ensureDirectories([deep]);
    expect(fs.existsSync(deep)).toBe(true);
  });

  test('does not throw when directory already exists', () => {
    const dir = path.join(root, 'existing');
    fs.mkdirSync(dir);
    expect(() => ensureDirectories([dir])).not.toThrow();
    expect(fs.existsSync(dir)).toBe(true);
  });

  test('handles empty array without error', () => {
    expect(() => ensureDirectories([])).not.toThrow();
  });

  test('creates only the missing dirs when some already exist', () => {
    const existing = path.join(root, 'yes');
    const missing = path.join(root, 'no');
    fs.mkdirSync(existing);

    ensureDirectories([existing, missing]);
    expect(fs.existsSync(existing)).toBe(true);
    expect(fs.existsSync(missing)).toBe(true);
  });
});
