const path = require('path');
const { closestMaiaModel } = require('../app/functions');

const MODELS_DIR = path.join(__dirname, '..', 'models');

describe('closestMaiaModel', () => {
  // 1520 is 20 away from 1500 and 80 away from 1600, so 1500 is selected
  test('picks nearest bracket when closer above', () => {
    const res = closestMaiaModel(1520, MODELS_DIR);
    expect(res.elo).toBe(1500);
    expect(res.filename).toBe('maia-1500.pb.gz');
    expect(res.path).toBe(path.join(MODELS_DIR, 'maia-1500.pb.gz'));
  });

  // ELO far below the lowest bracket (1100) should go to 1100
  test('picks lowest bracket when below minimum', () => {
    const res = closestMaiaModel(500, MODELS_DIR);
    expect(res.elo).toBe(1100);
    expect(res.filename).toBe('maia-1100.pb.gz');
    expect(res.path).toBe(path.join(MODELS_DIR, 'maia-1100.pb.gz'));
  });

  // ELO far above the highest bracket (1900) should go to 1900
  test('picks highest bracket when above maximum', () => {
    const res = closestMaiaModel(2500, MODELS_DIR);
    expect(res.elo).toBe(1900);
    expect(res.filename).toBe('maia-1900.pb.gz');
    expect(res.path).toBe(path.join(MODELS_DIR, 'maia-1900.pb.gz'));
  });

  // Negative ELO should still resolve to the lowest bracket (1100)
  test('picks lowest bracket for negative ELO', () => {
    const res = closestMaiaModel(-300, MODELS_DIR);
    expect(res.elo).toBe(1100);
    expect(res.filename).toBe('maia-1100.pb.gz');
    expect(res.path).toBe(path.join(MODELS_DIR, 'maia-1100.pb.gz'));
  });
});
