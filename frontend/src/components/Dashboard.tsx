import { useNavigate } from 'react-router';
import { Play, Settings, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { statsAPI, trainingAPI } from '../services/api';

interface UserStats {
  games_uploaded: number;
  models_trained: number;
  games_played: number;
}

interface Model {
  model_id: string;
  model_name: string;
  architecture: string;
  created_at: string;
  is_active: boolean;
  metadata: {
    epochs_trained?: number;
    best_val_loss?: number;
    training_games?: number;
  };
}

export function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load user stats
      const statsResponse = await statsAPI.getUserStats();
      setStats(statsResponse.data);

      // Load trained models
      const modelsResponse = await trainingAPI.getModels();
      setModels(modelsResponse.data.models);

    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleActivateModel = async (modelId: string) => {
    try {
      await trainingAPI.activateModel(modelId);
      // Reload models to update active status
      const modelsResponse = await trainingAPI.getModels();
      setModels(modelsResponse.data.models);
    } catch (err: any) {
      console.error('Failed to activate model:', err);
      setError('Failed to activate model');
    }
  };
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Find active model
  const activeModel = models.find(m => m.is_active);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A3B7A] mx-auto mb-4"></div>
          <p className="text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-medium mb-1">Error Loading Dashboard</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl text-[#4A3B7A] mb-2">Your Dashboard</h1>
          <p className="text-slate-600">Track your progress and manage your models</p>
        </div>
        <button
          onClick={() => navigate('/play')}
          disabled={!activeModel}
          className={`px-6 py-3 rounded-lg transition-colors flex items-center gap-2 ${
            activeModel
              ? 'bg-[#4A3B7A] text-white hover:bg-[#3D3066]'
              : 'bg-slate-300 text-slate-500 cursor-not-allowed'
          }`}
        >
          <Play className="w-5 h-5" />
          Play Game
        </button>
      </div>

      {/* No Active Model Warning */}
      {!activeModel && models.length === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-amber-800 font-medium mb-2">No Model Available</h3>
          <p className="text-amber-700 text-sm mb-4">
            You need to upload games and train a model before you can play.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/import')}
              className="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 transition-colors text-sm"
            >
              Upload Games
            </button>
            <button
              onClick={() => navigate('/training')}
              className="bg-white text-amber-800 px-4 py-2 rounded-lg border border-amber-300 hover:bg-amber-50 transition-colors text-sm"
            >
              Go to Training
            </button>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Games Uploaded</span>
            <Calendar className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">{stats?.games_uploaded || 0}</div>
          <div className="text-xs text-slate-600">From Chess.com/Lichess</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Models Trained</span>
            <TrendingUp className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">{stats?.models_trained || 0}</div>
          <div className="text-xs text-slate-600">Neural networks</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Games Played</span>
            <Play className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">{stats?.games_played || 0}</div>
          <div className="text-xs text-slate-600">Against your bot</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Active Model</span>
            <Settings className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-xl text-[#4A3B7A] mb-1 truncate">
            {activeModel ? activeModel.model_name : 'None'}
          </div>
          <div className="text-xs text-slate-600">
            {activeModel ? activeModel.architecture : 'Train a model'}
          </div>
        </div>
      </div>

      {/* Active Model Details */}
      {activeModel && (
        <div className="bg-white rounded-lg p-8 shadow-sm border border-slate-200">
          <h2 className="text-sm tracking-wide text-purple-800 mb-6">ACTIVE MODEL</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg mb-3 text-[#4A3B7A]">{activeModel.model_name}</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Architecture:</span>
                  <span className="text-slate-900">{activeModel.architecture}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Training Date:</span>
                  <span className="text-slate-900">
                    {new Date(activeModel.created_at).toLocaleDateString()}
                  </span>
                </div>
                {activeModel.metadata.epochs_trained && (
                  <div className="flex justify-between">
                    <span className="text-slate-600">Epochs:</span>
                    <span className="text-slate-900">{activeModel.metadata.epochs_trained}</span>
                  </div>
                )}
                {activeModel.metadata.training_games && (
                  <div className="flex justify-between">
                    <span className="text-slate-600">Training Games:</span>
                    <span className="text-slate-900">{activeModel.metadata.training_games}</span>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm mb-3">Performance</h3>
              {activeModel.metadata.best_val_loss && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Validation Loss:</span>
                    <span className="text-slate-900">
                      {activeModel.metadata.best_val_loss.toFixed(4)}
                    </span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full">
                    <div 
                      className="h-full bg-[#4A3B7A] rounded-full" 
                      style={{ width: `${Math.max(10, 100 - activeModel.metadata.best_val_loss * 100)}%` }}
                    ></div>
                  </div>
                </div>
              )}
              <button
                onClick={() => navigate('/training')}
                className="mt-4 text-sm text-[#4A3B7A] hover:underline flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                Manage Models
              </button>
            </div>
          </div>
        </div>
      )}

      {/* All Models */}
      {models.length > 0 && (
        <div className="bg-white rounded-lg p-8 shadow-sm border border-slate-200">
          <h2 className="text-sm tracking-wide text-purple-800 mb-6">YOUR MODELS</h2>
          
          <div className="space-y-3">
            {models.map((model) => (
              <div 
                key={model.model_id}
                className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${
                  model.is_active 
                    ? 'border-[#4A3B7A] bg-purple-50' 
                    : 'border-slate-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-center gap-4">
                  {model.is_active && (
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  )}
                  <div>
                    <div className="text-sm mb-1 text-slate-900">{model.model_name}</div>
                    <div className="text-xs text-slate-500">
                      {model.architecture} • {new Date(model.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-6">
                  {model.metadata.training_games && (
                    <div className="text-center">
                      <div className="text-xs text-slate-600 mb-1">Games</div>
                      <div className="text-sm text-slate-900">{model.metadata.training_games}</div>
                    </div>
                  )}
                  
                  {model.metadata.best_val_loss && (
                    <div className="text-center">
                      <div className="text-xs text-slate-600 mb-1">Loss</div>
                      <div className="text-sm text-slate-900">
                        {model.metadata.best_val_loss.toFixed(3)}
                      </div>
                    </div>
                  )}
                  
                  {model.is_active ? (
                    <span className="text-sm text-green-600 font-medium">Active</span>
                  ) : (
                    <button 
                      onClick={() => handleActivateModel(model.model_id)}
                      className="text-sm text-[#4A3B7A] hover:underline"
                    >
                      Activate
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <button
          onClick={() => navigate('/import')}
          className="bg-white border border-slate-200 rounded-lg p-6 hover:border-purple-300 transition-colors text-left"
        >
          <h3 className="text-lg mb-2 text-[#4A3B7A]">Upload More Games</h3>
          <p className="text-sm text-slate-600">
            Import games from Chess.com or Lichess to improve your model
          </p>
        </button>

        <button
          onClick={() => navigate('/training')}
          className="bg-white border border-slate-200 rounded-lg p-6 hover:border-purple-300 transition-colors text-left"
        >
          <h3 className="text-lg mb-2 text-[#4A3B7A]">Train New Model</h3>
          <p className="text-sm text-slate-600">
            Create a new model with your latest game data
          </p>
        </button>
      </div>
    </div>
  );
}

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl text-[#4A3B7A] mb-2">Your Dashboard</h1>
          <p className="text-slate-600">Track your progress against your mirror bot</p>
        </div>
        <button
          onClick={() => navigate('/play')}
          className="bg-[#4A3B7A] text-white px-6 py-3 rounded-lg hover:bg-[#3D3066] transition-colors flex items-center gap-2"
        >
          <Play className="w-5 h-5" />
          Play Game
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Games Played</span>
            <Calendar className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">47</div>
          <div className="text-xs text-green-600">+4 this week</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Win Rate</span>
            <TrendingUp className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">62%</div>
          <div className="text-xs text-green-600">+5% vs last month</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Avg Similarity</span>
            <Settings className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">85%</div>
          <div className="text-xs text-slate-600">Mirror accuracy</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-slate-600">Current Streak</span>
            <Play className="w-5 h-5 text-[#4A3B7A]" />
          </div>
          <div className="text-3xl text-[#4A3B7A] mb-1">3</div>
          <div className="text-xs text-green-600">Wins in a row</div>
        </div>
      </div>

      {/* Playing Style Overview */}
      <div className="bg-white rounded-lg p-8 shadow-sm border border-slate-200">
        <h2 className="text-sm tracking-wide text-purple-800 mb-6">YOUR PLAYING STYLE</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <div className="flex gap-3 flex-wrap mb-4">
              <span className="px-4 py-2 border-2 border-[#4A3B7A] text-[#4A3B7A] rounded-lg text-sm">
                Aggressive
              </span>
              <span className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg text-sm">
                Tactical
              </span>
              <span className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg text-sm">
                Central Control
              </span>
            </div>
            <p className="text-sm text-slate-600">
              You favor sharp, attacking lines with early piece development. You're comfortable
              sacrificing material for positional advantages.
            </p>
          </div>

          <div>
            <h3 className="text-sm mb-3">Preferred Openings</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Sicilian Defense</span>
                <span className="text-slate-500">38%</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full">
                <div className="h-full bg-[#4A3B7A] rounded-full" style={{ width: '38%' }}></div>
              </div>
              <div className="flex justify-between text-sm">
                <span>Ruy López</span>
                <span className="text-slate-500">25%</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full">
                <div className="h-full bg-[#4A3B7A] rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Games */}
      <div className="bg-white rounded-lg p-8 shadow-sm border border-slate-200">
        <h2 className="text-sm tracking-wide text-purple-800 mb-6">RECENT GAMES</h2>
        
        <div className="space-y-4">
          {recentGames.map((game) => (
            <div key={game.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:border-purple-300 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`w-2 h-2 rounded-full ${
                  game.result === 'Win' ? 'bg-green-500' : 
                  game.result === 'Loss' ? 'bg-red-500' : 
                  'bg-slate-400'
                }`}></div>
                <div>
                  <div className="text-sm mb-1">{game.date}</div>
                  <div className="text-xs text-slate-500">{game.moves} moves</div>
                </div>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-sm text-slate-600 mb-1">Result</div>
                  <div className={`text-sm ${
                    game.result === 'Win' ? 'text-green-600' : 
                    game.result === 'Loss' ? 'text-red-600' : 
                    'text-slate-600'
                  }`}>{game.result}</div>
                </div>
                
                <div className="text-center">
                  <div className="text-sm text-slate-600 mb-1">Similarity</div>
                  <div className="text-sm text-[#4A3B7A]">{game.similarity}%</div>
                </div>
                
                <button className="text-sm text-[#4A3B7A] hover:underline">
                  View Report
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bot Settings Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-sm mb-2">Bot Configuration</h3>
            <p className="text-sm text-slate-600">
              75% human-like • Opening repertoire matching enabled
            </p>
          </div>
          <button className="text-sm text-[#4A3B7A] hover:underline flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Adjust Settings
          </button>
        </div>
      </div>
    </div>
  );
}
