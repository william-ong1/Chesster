const path = require('path');
const fs = require('fs');
const os = require('os');
const { chmodBinaries } = require('../app/functions');

const isWindows = process.platform === 'win32';

function makeTempRoot() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'chmodbin-'));
}

function cleanup(root) {
  fs.rmSync(root, { recursive: true, force: true });
}

describe('chmodBinaries', () => {
  let root;
  let binDir;

  beforeEach(() => {
    root = makeTempRoot();
    binDir = path.join(root, 'bin');
    fs.mkdirSync(binDir);
  });

  afterEach(() => {
    cleanup(root);
  });

  test('sets 755 on all files in the directory', () => {
    const files = ['lc0', 'pgn-extract', 'tool'];
    files.forEach(f => fs.writeFileSync(path.join(binDir, f), '', { mode: 0o644 }));

    chmodBinaries(binDir);

    if (!isWindows) {
      files.forEach(f => {
        const mode = fs.statSync(path.join(binDir, f)).mode & 0o777;
        expect(mode).toBe(0o755);
      });
    }
  });

  test('does not throw when binDir does not exist', () => {
    const missing = path.join(root, 'nope');
    expect(() => chmodBinaries(missing)).not.toThrow();
  });

  test('handles an empty directory without error', () => {
    expect(() => chmodBinaries(binDir)).not.toThrow();
  });

  test('sets 755 on a single file', () => {
    fs.writeFileSync(path.join(binDir, 'solo'), '', { mode: 0o600 });

    chmodBinaries(binDir);

    if (!isWindows) {
      const mode = fs.statSync(path.join(binDir, 'solo')).mode & 0o777;
      expect(mode).toBe(0o755);
    }
  });

  test('handles files with various initial permissions', () => {
    const cases = [
      { name: 'read-only', mode: 0o444 },
      { name: 'no-perms', mode: 0o000 },
      { name: 'already-755', mode: 0o755 },
    ];
    cases.forEach(c => fs.writeFileSync(path.join(binDir, c.name), '', { mode: c.mode }));

    chmodBinaries(binDir);

    if (!isWindows) {
      cases.forEach(c => {
        const mode = fs.statSync(path.join(binDir, c.name)).mode & 0o777;
        expect(mode).toBe(0o755);
      });
    }
  });
});
