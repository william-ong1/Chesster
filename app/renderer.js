'use strict';

// ─── State ────────────────────────────────────────────────────────────────────

let selectedPgnPath = null;
let isTraining      = false;
let engineLoaded    = false;
let playerSide      = 'white';
let boardFlipped    = false;
let game            = null;
let selectedSquare  = null;
let legalMoves      = [];
let lastMove        = null;
let engineThinking  = false;

// ─── Chess piece unicode ───────────────────────────────────────────────────────

const PIECES = {
  wK: '♔', wQ: '♕', wR: '♖', wB: '♗', wN: '♘', wP: '♙',
  bK: '♚', bQ: '♛', bR: '♜', bB: '♝', bN: '♞', bP: '♟'
};

// ─── Navigation ───────────────────────────────────────────────────────────────

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('nav-btn--active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('view--active'));
    btn.classList.add('nav-btn--active');
    document.getElementById(`view-${view}`).classList.add('view--active');
    if (view === 'system') runSystemCheck();
    if (view === 'play')   refreshModelList();
  });
});

// ─── Train View ───────────────────────────────────────────────────────────────

// PGN drag-drop
const dropArea  = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');

document.getElementById('browseBtn').addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setPgn(fileInput.files[0].path || fileInput.files[0].name);
});

dropArea.addEventListener('dragover', e => {
  e.preventDefault();
  dropArea.classList.add('drop-area--over');
});
dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drop-area--over'));
dropArea.addEventListener('drop', e => {
  e.preventDefault();
  dropArea.classList.remove('drop-area--over');
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.pgn')) setPgn(file.path);
});

dropArea.addEventListener('click', async e => {
  if (e.target.id === 'browseBtn') return;
  const p = await window.api.openPgn();
  if (p) setPgn(p);
});

function setPgn(p) {
  selectedPgnPath = p;
  const name = p.split('/').pop().split('\\').pop();
  document.getElementById('dropArea').style.display    = 'none';
  document.getElementById('pgnSelected').style.display = 'flex';
  document.getElementById('pgnName').textContent = name;
  document.getElementById('pgnPath').textContent = p;
  updateTrainBtn();
}

document.getElementById('clearPgnBtn').addEventListener('click', () => {
  selectedPgnPath = null;
  fileInput.value = '';
  document.getElementById('dropArea').style.display    = 'flex';
  document.getElementById('pgnSelected').style.display = 'none';
  updateTrainBtn();
});

// ELO input
const MAIA_ELOS = [1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900];

function closestElo(n) {
  return MAIA_ELOS.reduce((a, b) => Math.abs(b - n) < Math.abs(a - n) ? b : a);
}

document.getElementById('eloInput').addEventListener('input', async () => {
  const val = parseInt(document.getElementById('eloInput').value, 10);
  const el  = document.getElementById('eloResult');
  if (!val || val < 100 || val > 3000) {
    el.textContent = '';
    updateTrainBtn();
    return;
  }
  const closest  = closestElo(val);
  const { exists } = await window.api.checkModel(val);
  el.textContent  = `→ maia-${closest}.pb.gz ${exists ? '✓' : '✗ (not found in models/)'}`;
  el.style.color  = exists ? '#a78bfa' : '#f87171';
  updateTrainBtn();
});

document.getElementById('usernameInput').addEventListener('input', updateTrainBtn);

function updateTrainBtn() {
  const hasFile = !!selectedPgnPath;
  const hasUser = document.getElementById('usernameInput').value.trim().length > 0;
  const hasElo  = parseInt(document.getElementById('eloInput').value, 10) >= 100;
  document.getElementById('startTrainBtn').disabled = !(hasFile && hasUser && hasElo && !isTraining);
}

// ─── Progress bar ─────────────────────────────────────────────────────────────

function setProgressBar(percent) {
  const bar = document.getElementById('progressBar');
  const pct = document.getElementById('progressPct');
  if (!bar) return;
  const clamped = Math.max(0, Math.min(100, percent));
  bar.style.width = `${clamped}%`;
  if (pct) pct.textContent = `${clamped}%`;
}

function showProgressBar(visible) {
  const wrap = document.getElementById('progressWrap');
  if (wrap) wrap.style.display = visible ? 'flex' : 'none';
}

// ─── Collapsible terminal ─────────────────────────────────────────────────────

(function initTerminalToggle() {
  const toggle = document.getElementById('terminalToggle');
  const body   = document.getElementById('terminalBody');
  if (!toggle || !body) return;

  // Start collapsed
  body.classList.add('terminal-body--collapsed');
  toggle.textContent = '▶ Show terminal';

  toggle.addEventListener('click', () => {
    const collapsed = body.classList.toggle('terminal-body--collapsed');
    toggle.textContent = collapsed ? '▶ Show terminal' : '▼ Hide terminal';
    if (!collapsed) body.scrollTop = body.scrollHeight; // scroll to bottom when opening
  });
})();

// ─── Start training ───────────────────────────────────────────────────────────

document.getElementById('startTrainBtn').addEventListener('click', async () => {
  const username = document.getElementById('usernameInput').value.trim();
  const userElo  = parseInt(document.getElementById('eloInput').value, 10);

  isTraining = true;
  updateTrainBtn();
  clearTerminal();
  showProgressBar(true);
  setProgressBar(0);

  document.getElementById('trainingBanner').style.display = 'flex';

  window.api.removeListeners();

  window.api.onProgress(({ step, message, percent, type }) => {
    // Always update the terminal with every line
    appendTerminal(step, message);

    // Only update banner headline for 'status' type messages
    if (type === 'status' || type == null) {
      updateBanner(step, message);
    }

    // Update progress bar whenever a percent value is provided
    if (percent !== null && percent !== undefined) {
      setProgressBar(percent);
    }
  });

  window.api.onError(({ message }) => {
    appendTerminal('error', message);
    updateBanner('error', 'Training failed');
    isTraining = false;
    updateTrainBtn();
    showProgressBar(false);
  });

  await window.api.startTraining({ pgnPath: selectedPgnPath, username, userElo });
});

function updateBanner(step, message) {
  const stepLabels = {
    clean:  'Step 1 — Cleaning PGN',
    data:   'Step 2 — Generating Training Data',
    config: 'Step 2b — Building Config',
    train:  'Step 3 — Training Neural Network',
    done:   'Complete',
    error:  'Error'
  };
  document.getElementById('bannerStep').textContent = stepLabels[step] || step;
  document.getElementById('bannerMsg').textContent  = message.slice(0, 120);

  if (step === 'done') {
    isTraining = false;
    updateTrainBtn();
    setProgressBar(100);
    setTimeout(() => {
      document.getElementById('trainingBanner').style.display = 'none';
      showProgressBar(false);
    }, 2000);
    refreshModelList();
  }
}

function clearTerminal() {
  document.getElementById('terminalBody').innerHTML = '';
}

function appendTerminal(step, message) {
  const body = document.getElementById('terminalBody');
  const placeholder = body.querySelector('.terminal-placeholder');
  if (placeholder) placeholder.remove();

  const line = document.createElement('span');
  line.className = `terminal-line terminal-line--${step}`;
  line.textContent = message;
  body.appendChild(line);
  body.appendChild(document.createElement('br'));

  // Auto-scroll only if terminal is expanded
  if (!body.classList.contains('terminal-body--collapsed')) {
    body.scrollTop = body.scrollHeight;
  }
}

// ─── Play View ────────────────────────────────────────────────────────────────

async function refreshModelList() {
  const select = document.getElementById('modelSelect');
  const models = await window.api.listModels();
  select.innerHTML = '<option value="">select a model</option>';
  models.forEach(m => {
    const opt = document.createElement('option');
    opt.value       = m.path;
    opt.textContent = m.name;
    select.appendChild(opt);
  });
}

// Side selection
document.getElementById('playWhiteBtn').addEventListener('click', () => setSide('white'));
document.getElementById('playBlackBtn').addEventListener('click', () => setSide('black'));

function setSide(side) {
  playerSide = side;
  boardFlipped = side === 'black';
  document.getElementById('playWhiteBtn').classList.toggle('side-btn--active', side === 'white');
  document.getElementById('playBlackBtn').classList.toggle('side-btn--active', side === 'black');
  if (game) renderBoard();
}

// Load engine
document.getElementById('loadEngineBtn').addEventListener('click', async () => {
  const modelPath = document.getElementById('modelSelect').value;
  if (!modelPath) return;

  const btn = document.getElementById('loadEngineBtn');
  btn.textContent = 'Loading...';
  btn.disabled    = true;

  // Unload previous engine first
  await window.api.unloadEngine();
  engineLoaded = false;

  const result = await window.api.loadEngine(modelPath);
  btn.disabled = false;

  if (result.ok) {
    engineLoaded = true;
    btn.textContent = '✓ Engine Loaded';
    document.getElementById('newGameBtn').disabled = false;
    document.getElementById('gameStatus').textContent = 'Engine ready. Start a new game.';
  } else {
    btn.textContent = 'Load Engine';
    btn.disabled    = false;
    document.getElementById('gameStatus').textContent = `Error: ${result.error}`;
  }
});

// Also reset button when model selection changes
document.getElementById('modelSelect').addEventListener('change', () => {
  engineLoaded = false;
  const btn = document.getElementById('loadEngineBtn');
  btn.textContent = 'Load Engine';
  btn.disabled    = false;
  document.getElementById('newGameBtn').disabled = true;
  document.getElementById('gameStatus').textContent = '';
  window.api.unloadEngine();
});

// New game
document.getElementById('newGameBtn').addEventListener('click', () => {
  game          = new Chess();
  selectedSquare = null;
  legalMoves    = [];
  lastMove      = null;
  boardFlipped  = playerSide === 'black';

  document.getElementById('moveLog').innerHTML = '';
  document.getElementById('gameStatus').textContent = '';

  renderBoard();
  renderCoords();

  // If player is black, engine moves first
  if (playerSide === 'black') {
    setTimeout(doEngineMove, 400);
  }
});

// Flip board
document.getElementById('flipBoardBtn').addEventListener('click', () => {
  boardFlipped = !boardFlipped;
  renderBoard();
  renderCoords();
});

// ─── Chess board ───────────────────────────────────────────────────────────────

function renderBoard() {
  const board = document.getElementById('chessBoard');
  board.innerHTML = '';

  const ranks = boardFlipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const files = boardFlipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];

  for (const rank of ranks) {
    for (const file of files) {
      const sq    = squareName(file, rank);
      const isLight = (file + rank) % 2 !== 0;
      const div   = document.createElement('div');

      div.className = `square square--${isLight ? 'light' : 'dark'}`;
      div.dataset.sq = sq;

      // Highlights
      if (selectedSquare === sq) div.classList.add('square--selected');

      if (lastMove) {
        if (lastMove.from === sq) div.classList.add('square--last-move-from');
        if (lastMove.to   === sq) div.classList.add('square--last-move-to');
      }

      // Legal move dots
      if (legalMoves.includes(sq)) {
        const piece = game.get(sq);
        div.classList.add(piece ? 'square--legal-capture' : 'square--legal');
      }

      // Check highlight
      if (game && game.in_check()) {
        const turn = game.turn() === 'w' ? 'w' : 'b';
        const kingSq = findKing(turn);
        if (kingSq === sq) div.classList.add('square--check');
      }

      // Piece
      if (game) {
        const piece = game.get(sq);
        if (piece) {
          const span = document.createElement('span');
          span.className = `piece piece--${piece.color === 'w' ? 'white' : 'black'}`;
          span.textContent = PIECES[piece.color + piece.type.toUpperCase()];
          div.appendChild(span);
        }
      }

      div.addEventListener('click', () => onSquareClick(sq));
      board.appendChild(div);
    }
  }
}

function squareName(file, rank) {
  return 'abcdefgh'[file] + (rank + 1);
}

function findKing(color) {
  for (const rank of ['1','2','3','4','5','6','7','8']) {
    for (const file of ['a','b','c','d','e','f','g','h']) {
      const sq = file + rank;
      const p  = game.get(sq);
      if (p && p.type === 'k' && p.color === color) return sq;
    }
  }
  return null;
}

function renderEmptyBoard() {
  // Render starting position visually but non-interactive
  const tempGame = new Chess();
  const board    = document.getElementById('chessBoard');
  board.innerHTML = '';

  const ranks = boardFlipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const files = boardFlipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];

  for (const rank of ranks) {
    for (const file of files) {
      const sq      = squareName(file, rank);
      const isLight = (file + rank) % 2 !== 0;
      const div     = document.createElement('div');
      div.className = `square square--${isLight ? 'light' : 'dark'}`;
      div.dataset.sq = sq;

      const piece = tempGame.get(sq);
      if (game) {
        const piece = game.get(sq);
        if (piece) {
          const span = document.createElement('span');
          span.className = `piece piece--${piece.color === 'w' ? 'white' : 'black'}`;
          span.textContent = PIECES[piece.color + piece.type.toUpperCase()];
          div.appendChild(span);
        }
      }

      div.addEventListener('click', () => showNoGameTooltip(div));
      board.appendChild(div);
    }
  }
}

let tooltipTimeout = null;

function showNoGameTooltip(targetEl) {
  // Don't show if game is active
  if (game && !game.game_over()) return;

  // Remove existing tooltip
  document.querySelectorAll('.board-tooltip').forEach(t => t.remove());
  if (tooltipTimeout) clearTimeout(tooltipTimeout);

  const tip = document.createElement('div');
  tip.className   = 'board-tooltip';
  tip.textContent = game && game.game_over()
    ? 'Game over — start a new game'
    : 'No game is active — press New Game';

  targetEl.appendChild(tip);
  tooltipTimeout = setTimeout(() => tip.remove(), 2000);
}

function renderCoords() {
  const files = boardFlipped
    ? ['h','g','f','e','d','c','b','a']
    : ['a','b','c','d','e','f','g','h'];
  const ranks = boardFlipped
    ? ['1','2','3','4','5','6','7','8']
    : ['8','7','6','5','4','3','2','1'];

  const fileEl = document.getElementById('fileCoords');
  const rankEl = document.getElementById('rankCoords');
  fileEl.innerHTML = files.map(f => `<span>${f}</span>`).join('');
  rankEl.innerHTML = ranks.map(r => `<span>${r}</span>`).join('');
}

function onSquareClick(sq) {
  if (!game) { showNoGameTooltip(document.querySelector(`[data-sq="${sq}"]`)); return; }
  if (game.game_over()) { showNoGameTooltip(document.querySelector(`[data-sq="${sq}"]`)); return; }
  if (engineThinking) return;
  const isPlayerTurn =
    (game.turn() === 'w' && playerSide === 'white') ||
    (game.turn() === 'b' && playerSide === 'black');
  if (!isPlayerTurn) return;
  const piece = game.get(sq);
  if (selectedSquare) {
    if (legalMoves.includes(sq)) {
      attemptMove(selectedSquare, sq);
    } else if (piece && piece.color === game.turn()) {
      selectedSquare = sq;
      legalMoves = getLegalMovesForSquare(sq);
      renderBoard();
    } else {
      selectedSquare = null;
      legalMoves = [];
      renderBoard();
    }
  } else {
    if (piece && piece.color === game.turn()) {
      selectedSquare = sq;
      legalMoves = getLegalMovesForSquare(sq);
      renderBoard();
    }
  }
}

function getLegalMovesForSquare(sq) {
  return game.moves({ square: sq, verbose: true }).map(m => m.to);
}

function attemptMove(from, to) {
  const piece = game.get(from);

  // Check for promotion
  if (piece && piece.type === 'p') {
    const toRank = parseInt(to[1], 10);
    if ((piece.color === 'w' && toRank === 8) || (piece.color === 'b' && toRank === 1)) {
      showPromotion(from, to);
      return;
    }
  }

  applyMove(from, to);
}

function applyMove(from, to, promotion = null) {
  const moveObj = { from, to };
  if (promotion) moveObj.promotion = promotion;

  const result = game.move(moveObj);
  if (!result) return;

  lastMove      = { from, to };
  selectedSquare = null;
  legalMoves    = [];

  addMoveToLog(result);
  renderBoard();
  checkGameOver();

  if (!game.game_over()) {
    setTimeout(doEngineMove, 300);
  }
}

async function doEngineMove() {
  if (!engineLoaded || game.game_over()) return;
  engineThinking = true;
  document.getElementById('gameStatus').textContent = 'Engine is thinking...';

  const fen = game.fen();
  const result = await window.api.getMove(fen);

  engineThinking = false;

  if (result.error) {
    document.getElementById('gameStatus').textContent = `Engine error: ${result.error}`;
    return;
  }

  const move = result.move;
  if (!move || move === '(none)') return;

  const from = move.slice(0, 2);
  const to   = move.slice(2, 4);
  const promo = move.length > 4 ? move[4] : null;

  const applied = game.move({ from, to, promotion: promo || undefined });
  if (!applied) return;

  lastMove = { from, to };
  addMoveToLog(applied);
  renderBoard();
  checkGameOver();

  if (!game.game_over()) {
    document.getElementById('gameStatus').textContent = 'Your turn';
  }
}

function addMoveToLog(move) {
  const log = document.getElementById('moveLog');
  const num = Math.ceil(game.history().length / 2);

  if (move.color === 'w') {
    const numEl = document.createElement('span');
    numEl.className   = 'move-log__num';
    numEl.textContent = `${num}.`;

    const wEl = document.createElement('span');
    wEl.className   = 'move-log__move move-log__move--current';
    wEl.textContent = move.san;

    // Placeholder for black's move
    const bEl = document.createElement('span');
    bEl.className   = 'move-log__move';
    bEl.id          = `move-b-${num}`;
    bEl.textContent = '';

    log.appendChild(numEl);
    log.appendChild(wEl);
    log.appendChild(bEl);
  } else {
    const el = document.getElementById(`move-b-${num}`);
    if (el) {
      el.textContent = move.san;
      el.classList.add('move-log__move--current');
    }
  }

  log.scrollTop = log.scrollHeight;
}

function checkGameOver() {
  const status = document.getElementById('gameStatus');
  if (game.in_checkmate()) {
    const winner = game.turn() === 'w' ? 'Black' : 'White';
    status.textContent = `♚ Checkmate — ${winner} wins!`;
  } else if (game.in_stalemate()) {
    status.textContent = '½ Stalemate — Draw';
  } else if (game.in_draw()) {
    status.textContent = '½ Draw';
  } else if (game.in_check()) {
    status.textContent = '⚠ Check!';
  } else {
    status.textContent = game.turn() === 'w' ? 'White to move' : 'Black to move';
  }
}

// ── Promotion ─────────────────────────────────────────────────────────────────

function showPromotion(from, to) {
  const overlay = document.getElementById('promotionOverlay');
  const container = document.getElementById('promotionPieces');
  const color = game.turn();

  const pieces = [
    { type: 'q', label: color === 'w' ? '♕' : '♛' },
    { type: 'r', label: color === 'w' ? '♖' : '♜' },
    { type: 'b', label: color === 'w' ? '♗' : '♝' },
    { type: 'n', label: color === 'w' ? '♘' : '♞' },
  ];

  container.innerHTML = '';
  pieces.forEach(({ type, label }) => {
    const div = document.createElement('div');
    div.className   = 'promotion-piece';
    div.textContent = label;
    div.addEventListener('click', () => {
      overlay.style.display = 'none';
      selectedSquare = null;
      legalMoves     = [];
      applyMove(from, to, type);
    });
    container.appendChild(div);
  });

  overlay.style.display = 'flex';
}

// ─── System check ─────────────────────────────────────────────────────────────

async function runSystemCheck() {
  const grid = document.getElementById('systemGrid');
  grid.innerHTML = '<div class="check-placeholder">Running diagnostics...</div>';

  const checks = await window.api.checkSystem();
  grid.innerHTML = '';

  const labels = {
    lc0:            'lc0 Engine (v0.23.x)',
    docker:         'Docker',
    dockerImage:    'Docker Training Image',
    python3:        'Python 3',
    maiaIndividual: 'maia-individual repo',
    baseModels:     'Base Maia Models'
  };

  let allOk = true;

  Object.entries(checks).forEach(([key, { ok, path: p }]) => {
    if (!ok) allOk = false;
    const card = document.createElement('div');
    card.className = `check-card check-card--${ok ? 'ok' : 'fail'}`;
    card.innerHTML = `
      <div class="check-indicator check-indicator--${ok ? 'ok' : 'fail'}"></div>
      <div class="check-content">
        <div class="check-name">${labels[key] || key}</div>
        <div class="check-path">${p}</div>
      </div>
      <div class="check-status check-status--${ok ? 'ok' : 'fail'}">${ok ? '✓' : '✗'}</div>
    `;
    grid.appendChild(card);
  });

  const dot = document.getElementById('systemDot');
  dot.className = `system-dot system-dot--${allOk ? 'ok' : 'fail'}`;
}

document.getElementById('recheckBtn').addEventListener('click', runSystemCheck);

// ─── Init ─────────────────────────────────────────────────────────────────────

async function init() {
  game = null;
  renderCoords();
  renderEmptyBoard();
  await refreshModelList();

  // Setup overlay — now receives structured { message, percent, type }
  window.api.onSetupProgress(({ message, percent, type }) => {
    // Always update the text
    document.getElementById('setupMsg').textContent = message;

    // Drive the setup overlay progress bar if present
    const bar = document.getElementById('setupProgressBar');
    if (bar && percent !== null && percent !== undefined) {
      bar.style.width = `${Math.max(0, Math.min(100, percent))}%`;
    }
  });

  window.api.onSetupDone(() => {
    document.getElementById('setupOverlay').classList.add('setup-overlay--hidden');
  });

  window.api.onSetupError(msg => {
    document.getElementById('setupMsg').textContent = `Error: ${msg}`;
  });

  window.api.onDockerNeeded(() => {
    document.getElementById('setupSpinner').style.display = 'none';
    document.getElementById('setupMsg').textContent =
      'Docker is required but is not installed.';
    const link = document.getElementById('setupDockerLink');
    link.style.display = 'block';
    link.addEventListener('click', (e) => {
      e.preventDefault();
      window.api.openExternal('https://www.docker.com/products/docker-desktop/');
    });
  });

  // Quick silent system check for the status dot
  const checks = await window.api.checkSystem();
  const allOk = Object.values(checks).every(c => c.ok);
  const dot = document.getElementById('systemDot');
  dot.className = `system-dot system-dot--${allOk ? 'ok' : 'fail'}`;
}

init();