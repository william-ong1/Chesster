'use strict';

/**
 * Runs evaluation (prediction_generator) on the test set after training completes.
 * Prints evaluation results to console and sends them to the UI via send().
 *
 * @param {Object} opts
 * @param {string} opts.outputDir - Session output directory (host path)
 * @param {string} opts.username - Player username
 * @param {string} opts.latestModelPath - Full path to trained model .pb.gz
 * @param {string} opts.finalModelsDir - Directory containing final_models
 * @param {string} opts.maiaDir - maia-individual directory path
 * @param {string} opts.imageName - Docker image name
 * @param {string} opts.root - Project root
 * @param {function(string, string, number, string)} opts.send - (step, message, frac, type) => void
 * @param {Object} [deps] - Optional dependency injection for testing
 * @param {Function} [deps.spawn] - child_process.spawn
 * @param {Object} [deps.fs] - fs module
 * @param {Object} [deps.path] - path module
 * @returns {Promise<void>}
 */
async function runEvaluationAfterTraining(opts, deps = {}) {
  const {
    outputDir,
    username,
    latestModelPath,
    finalModelsDir,
    maiaDir,
    imageName,
    root,
    send,
  } = opts;

  const path = deps.path || require('path');
  const fs = deps.fs || require('fs');
  const spawn = deps.spawn || require('child_process').spawn;

  const playerDir = path.join(outputDir, username);
  const testWhiteCsv = path.join(playerDir, 'csvs', 'test_white.csv.bz2');
  const testBlackCsv = path.join(playerDir, 'csvs', 'test_black.csv.bz2');
  const hasTestSet = fs.existsSync(testWhiteCsv) || fs.existsSync(testBlackCsv);

  if (!hasTestSet) {
    console.log('[Eval] Skipping: no test CSVs at', testWhiteCsv, 'or', testBlackCsv);
  }
  if (!latestModelPath) {
    console.log('[Eval] Skipping: no trained model found in final_models');
  }

  if (!latestModelPath || !hasTestSet) {
    return;
  }

  send('train', 'Running evaluation on test set...', 0.98, 'status');

  try {
    const modelPathInContainer = path
      .join('/maia-individual', 'final_models', path.relative(finalModelsDir, latestModelPath))
      .replace(/\\/g, '/');

    const evalProc = spawn(
      'docker',
      [
        'run',
        '--rm',
        '-v',
        `${maiaDir}:/maia-individual`,
        '-v',
        `${outputDir}:/session`,
        '-w',
        '/maia-individual',
        imageName,
        'conda',
        'run',
        '--no-capture-output',
        '-n',
        'transfer_chess',
        'python',
        '-u',
        '3-analysis/run_eval_and_print.py',
        modelPathInContainer,
        '/session',
        username,
      ],
      { cwd: root }
    );

    evalProc.stdout.on('data', (d) => {
      const txt = d.toString();
      console.log(txt.trim());
      send('train', txt.trim(), 0.99, 'log');
    });

    evalProc.stderr.on('data', (d) => {
      console.error(d.toString().trim());
    });

    await new Promise((res, rej) => {
      evalProc.on('close', (code) => {
        if (code === 0) {
          res();
        } else {
          rej(new Error(`Evaluation exited with code ${code}`));
        }
      });
    });
  } catch (err) {
    console.warn('[Eval] Evaluation failed:', err.message);
    send('train', `Evaluation skipped: ${err.message}`, 0.99, 'status');
  }
}

module.exports = { runEvaluationAfterTraining };
