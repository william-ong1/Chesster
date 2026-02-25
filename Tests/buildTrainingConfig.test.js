const fs = require('fs');
const { buildTrainingConfig } = require('../app/functions');

jest.mock('fs');

describe('buildTrainingConfig', () => {
  const templatePath = '/mock/maia-individual/2-training/final_config.yaml';
  const modelFilename = 'maia-1500.pb.gz';

  beforeEach(() => {
    jest.resetAllMocks();
  });

  test('replaces placeholders correctly', () => {
    const yamlContent = `
      data:
        path: "path to player data"
      model:
        path: "maia-1234"
    `;

    fs.existsSync.mockReturnValue(true);
    fs.readFileSync.mockReturnValue(yamlContent);

    const result = buildTrainingConfig(templatePath, modelFilename);

    // Check that player data path is replaced
    expect(result).toContain(`path: '/session'`);

    // Check that model path is replaced
    expect(result).toContain(`path: "/models/${modelFilename}"`);

    // Original text should no longer exist
    expect(result).not.toContain(`path to player data`);
    expect(result).not.toContain(`maia-1234`);
  });

  test('throws an error if template file does not exist', () => {
    fs.existsSync.mockReturnValue(false);

    expect(() => buildTrainingConfig(templatePath, modelFilename))
      .toThrow('final_config.yaml not found in maia-individual/2-training/');
  });
});