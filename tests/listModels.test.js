const fs = require('fs');
const path = require('path');
const { listModels } =  require('../app/functions');

// Mock fs methods
jest.mock('fs');

describe('listModels', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  test('lists .pb.gz files from individual and base directories, sorted by mtime', () => {
    const individualDir = '/mock/individual';
    const baseDir = '/mock/base';

    // Mock fs.existsSync
    fs.existsSync.mockImplementation((p) => {
      return p === individualDir || p === baseDir;
    });

    // Mock readdirSync
    fs.readdirSync.mockImplementation((p) => {
      if (p === individualDir) return ['a.pb.gz', 'b.pb.gz', 'ignore.txt'];
      if (p === baseDir) return ['c.pb.gz', 'd.pb.gz', 'note.doc'];
      return [];
    });

    // Mock statSync to give different mtimes
    fs.statSync.mockImplementation((p) => {
      const filename = path.basename(p);
      return {
        mtime: filename === 'a.pb.gz' ? new Date('2023-01-01') :
               filename === 'b.pb.gz' ? new Date('2023-02-01') :
               filename === 'c.pb.gz' ? new Date('2023-03-01') :
               filename === 'd.pb.gz' ? new Date('2023-01-15') :
               new Date('2020-01-01'),
      };
    });

    const result = listModels(baseDir, individualDir);

    // Should include only .pb.gz files, sorted by mtime descending
    expect(result.map(f => f.name)).toEqual(['b.pb.gz', 'a.pb.gz', 'c.pb.gz', 'd.pb.gz']);

    // Each entry has correct path
    expect(result.map(f => f.path)).toEqual([
      path.join(individualDir, 'b.pb.gz'),
      path.join(individualDir, 'a.pb.gz'),
      path.join(baseDir, 'c.pb.gz'),
      path.join(baseDir, 'd.pb.gz'),
    ]);
  });

  test('handles missing individual directory gracefully', () => {
    const individualDir = '/mock/individual';
    const baseDir = '/mock/base';

    fs.existsSync.mockImplementation((p) => p === baseDir);
    fs.readdirSync.mockImplementation((p) => p === baseDir ? ['x.pb.gz'] : []);

    fs.statSync.mockReturnValue({ mtime: new Date('2023-04-01') });

    const result = listModels(baseDir, individualDir);

    expect(result.map(f => f.name)).toEqual(['x.pb.gz']);
    expect(result[0].path).toBe(path.join(baseDir, 'x.pb.gz'));
  });

  test('handles no .pb.gz files', () => {
    const individualDir = '/mock/individual';
    const baseDir = '/mock/base';

    fs.existsSync.mockReturnValue(true);
    fs.readdirSync.mockReturnValue(['file.txt', 'other.doc']);
    fs.statSync.mockReturnValue({ mtime: new Date() });

    const result = listModels(baseDir, individualDir);

    expect(result).toEqual([]);
  });
});