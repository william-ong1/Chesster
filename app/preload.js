'use strict';
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  checkSystem:   ()           => ipcRenderer.invoke('system:check'),
  openPgn:       ()           => ipcRenderer.invoke('dialog:open-pgn'),
  listModels:    ()           => ipcRenderer.invoke('models:list'),
  checkModel:    (elo)        => ipcRenderer.invoke('models:check', { elo }),
  startTraining: (opts)       => ipcRenderer.invoke('training:start', opts),
  loadEngine:    (weightsPath)=> ipcRenderer.invoke('engine:load', { weightsPath }),
  getMove:       (fen)        => ipcRenderer.invoke('engine:move', { fen }),
  unloadEngine:  ()           => ipcRenderer.invoke('engine:unload'),
  openExternal:  (url)        => ipcRenderer.invoke('shell:open', { url }),
  onSetupProgress: (cb) => ipcRenderer.on('setup:progress', (_, msg) => cb(msg)),
  onSetupDone:     (cb) => ipcRenderer.on('setup:done', () => cb()),
  onSetupError:    (cb) => ipcRenderer.on('setup:error', (_, msg) => cb(msg)),
  onDockerNeeded: (cb) => ipcRenderer.on('setup:docker-needed', () => cb()),

  onProgress: (cb) => {
    ipcRenderer.on('training:progress', (_, data) => cb(data));
  },
  onError: (cb) => {
    ipcRenderer.on('training:error', (_, data) => cb(data));
  },
  removeListeners: () => {
    ipcRenderer.removeAllListeners('training:progress');
    ipcRenderer.removeAllListeners('training:error');
  }
});