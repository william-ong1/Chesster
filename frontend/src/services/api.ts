// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
// Frontend API service layer for backend communication

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: (username: string, email: string, password: string) =>
    apiClient.post('/api/auth/register', { username, email, password }),
  
  login: (username: string, password: string) =>
    apiClient.post('/api/auth/login', { username, password }),
  
  verify: () =>
    apiClient.get('/api/auth/verify'),
};

// Upload API
export const uploadAPI = {
  uploadPGN: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/upload/pgn', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  importChessCom: (username: string, numGames: number = 100) =>
    apiClient.post('/api/upload/chesscom', { username, num_games: numGames }),
  
  importLichess: (username: string, numGames: number = 100) =>
    apiClient.post('/api/upload/lichess', { username, num_games: numGames }),
};

// Training API
export const trainingAPI = {
  startTraining: (params: {
    epochs: number;
    batchSize: number;
    learningRate: number;
    validationSplit: number;
    modelName: string;
  }) =>
    apiClient.post('/api/training/start', params),
  
  getStatus: (jobId: string) =>
    apiClient.get(`/api/training/status/${jobId}`),
  
  getModels: () =>
    apiClient.get('/api/training/models'),
  
  activateModel: (modelId: string) =>
    apiClient.post(`/api/training/activate/${modelId}`),
  
  deleteModel: (modelId: string) =>
    apiClient.delete(`/api/training/models/${modelId}`),
};

// Agent API
export const agentAPI = {
  getMove: (fen: string, depth: number = 3, modelId?: string) =>
    apiClient.post('/api/agent/move', { fen, depth, model_id: modelId }),
  
  evaluate: (fen: string, modelId?: string) =>
    apiClient.post('/api/agent/evaluate', { fen, model_id: modelId }),
  
  analyze: (fens: string[], modelId?: string) =>
    apiClient.post('/api/agent/analyze', { fens, model_id: modelId }),
  
  makeMove: (fen: string, move: string, promotion: string = 'q') =>
    apiClient.post('/api/agent/make-move', { fen, move, promotion }),
  
  getLegalMoves: (fen: string, square?: string) =>
    apiClient.post('/api/agent/legal-moves', { fen, square }),
};

// Stats API
export const statsAPI = {
  getUserStats: () =>
    apiClient.get('/api/stats/user'),
  
  getGameHistory: (limit: number = 50) =>
    apiClient.get(`/api/stats/games?limit=${limit}`),
};

export default apiClient;
