// (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Sparkles, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { trainingAPI, statsAPI } from '../../services/api';

interface TrainingParams {
  epochs: number;
  batchSize: number;
  learningRate: number;
  validationSplit: number;
  modelName: string;
}

interface TrainingStatus {
  status: string;
  current_epoch?: number;
  total_epochs?: number;
  current_loss?: number;
  best_loss?: number;
  estimated_time_remaining?: number;
  progress_percentage?: number;
}

export function Training() {
  const navigate = useNavigate();
  const [isTraining, setIsTraining] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [gamesCount, setGamesCount] = useState<number>(0);
  const [trainingParams, setTrainingParams] = useState<TrainingParams>({
    epochs: 50,
    batchSize: 32,
    learningRate: 0.001,
    validationSplit: 0.2,
    modelName: `model_${Date.now()}`
  });

  useEffect(() => {
    fetchGamesCount();
  }, []);

  useEffect(() => {
    if (jobId && isTraining) {
      const interval = setInterval(() => {
        pollTrainingStatus();
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(interval);
    }
  }, [jobId, isTraining]);

  const fetchGamesCount = async () => {
    try {
      const response = await statsAPI.getUserStats();
      setGamesCount(response.data.games_uploaded || 0);
    } catch (err: any) {
      console.error('Failed to fetch games count:', err);
    }
  };

  const pollTrainingStatus = async () => {
    if (!jobId) return;

    try {
      const response = await trainingAPI.getStatus(jobId);
      const newStatus = response.data;
      setStatus(newStatus);

      if (newStatus.status === 'completed') {
        setIsTraining(false);
        setTimeout(() => {
          navigate('/complete');
        }, 2000);
      } else if (newStatus.status === 'failed') {
        setIsTraining(false);
        setError(newStatus.error || 'Training failed');
      }
    } catch (err: any) {
      console.error('Failed to poll training status:', err);
      setError('Failed to get training status');
      setIsTraining(false);
    }
  };

  const startTraining = async () => {
    try {
      setError(null);
      setIsTraining(true);

      const response = await trainingAPI.startTraining(trainingParams);
      const { job_id } = response.data;
      setJobId(job_id);
      setStatus({ status: 'queued' });
    } catch (err: any) {
      console.error('Failed to start training:', err);
      setError(err.response?.data?.error || 'Failed to start training');
      setIsTraining(false);
    }
  };

  const getProgressSteps = () => {
    if (!status) {
      return [
        { label: 'Loading training data', completed: false, current: false },
        { label: 'Initializing model', completed: false, current: false },
        { label: 'Training neural network', completed: false, current: false },
        { label: 'Validating performance', completed: false, current: false },
        { label: 'Saving model', completed: false, current: false }
      ];
    }

    const progress = status.progress_percentage || 0;
    
    return [
      { label: 'Loading training data', completed: progress > 0, current: progress <= 10 && progress > 0 },
      { label: 'Initializing model', completed: progress > 10, current: progress <= 20 && progress > 10 },
      { label: 'Training neural network', completed: progress > 80, current: progress <= 80 && progress > 20 },
      { label: 'Validating performance', completed: progress > 90, current: progress <= 95 && progress > 80 },
      { label: 'Saving model', completed: progress === 100, current: progress > 95 && progress < 100 }
    ];
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  if (gamesCount < 10) {
    return (
      <div className="max-w-2xl mx-auto text-center space-y-8 py-16 animate-slide-in-right">
        <div className="w-20 h-20 bg-orange-500 rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="w-10 h-10 text-white" />
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl text-[#4A3B7A]">Not Enough Games</h1>
          <p className="text-slate-600 text-lg">
            You need at least 10 games to train a model
          </p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <p className="text-sm text-slate-700">
            <Info className="w-4 h-4 inline mr-2" />
            You currently have <span className="font-bold">{gamesCount} games</span>. Please import more games before training.
          </p>
        </div>

        <button
          onClick={() => navigate('/import')}
          className="bg-[#4A3B7A] text-white px-6 py-3 rounded-lg hover:bg-[#3D3066] transition-colors"
        >
          Import More Games
        </button>
      </div>
    );
  }

  if (!isTraining && !jobId) {
    return (
      <div className="max-w-2xl mx-auto space-y-8 py-16 animate-slide-in-right">
        <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto">
          <Sparkles className="w-10 h-10 text-white" />
        </div>

        <div className="space-y-4 text-center">
          <h1 className="text-4xl text-[#4A3B7A]">Configure Training</h1>
          <p className="text-slate-600 text-lg">
            Set training parameters for your model
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-800 font-medium mb-1">Training Error</h3>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg p-8 shadow-sm space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Model Name
              </label>
              <input
                type="text"
                value={trainingParams.modelName}
                onChange={(e) => setTrainingParams({ ...trainingParams, modelName: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-[#4A3B7A] focus:border-transparent"
                placeholder="my_chess_model"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Training Epochs: {trainingParams.epochs}
              </label>
              <input
                type="range"
                min="10"
                max="100"
                value={trainingParams.epochs}
                onChange={(e) => setTrainingParams({ ...trainingParams, epochs: parseInt(e.target.value) })}
                className="w-full"
              />
              <div className="text-xs text-slate-500 mt-1">More epochs = better accuracy but longer training time</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Batch Size: {trainingParams.batchSize}
              </label>
              <select
                value={trainingParams.batchSize}
                onChange={(e) => setTrainingParams({ ...trainingParams, batchSize: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-[#4A3B7A] focus:border-transparent"
              >
                <option value="16">16 (Slower, more accurate)</option>
                <option value="32">32 (Balanced)</option>
                <option value="64">64 (Faster, less accurate)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Learning Rate: {trainingParams.learningRate}
              </label>
              <select
                value={trainingParams.learningRate}
                onChange={(e) => setTrainingParams({ ...trainingParams, learningRate: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-[#4A3B7A] focus:border-transparent"
              >
                <option value="0.0001">0.0001 (Conservative)</option>
                <option value="0.001">0.001 (Recommended)</option>
                <option value="0.01">0.01 (Aggressive)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Validation Split: {(trainingParams.validationSplit * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="0.3"
                step="0.05"
                value={trainingParams.validationSplit}
                onChange={(e) => setTrainingParams({ ...trainingParams, validationSplit: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="text-xs text-slate-500 mt-1">
                {Math.floor(gamesCount * (1 - trainingParams.validationSplit))} games for training, 
                {Math.floor(gamesCount * trainingParams.validationSplit)} for validation
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-200">
            <div className="text-sm text-slate-600 mb-4">
              Training with <span className="text-[#4A3B7A] font-medium">{gamesCount} games</span>
            </div>
            <button
              onClick={startTraining}
              className="w-full bg-[#4A3B7A] text-white px-6 py-3 rounded-lg hover:bg-[#3D3066] transition-colors font-medium"
            >
              Start Training
            </button>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <p className="text-sm text-slate-700">
            <Info className="w-4 h-4 inline mr-2" />
            Training typically takes 5-15 minutes depending on the number of epochs and your system.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto text-center space-y-8 py-16 animate-slide-in-right">
      <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto animate-pulse">
        <Sparkles className="w-10 h-10 text-white" />
      </div>

      <div className="space-y-4">
        <h1 className="text-4xl text-[#4A3B7A]">Training Your Bot</h1>
        <p className="text-slate-600 text-lg">
          Building your personalized chess opponent...
        </p>
        {status?.progress_percentage !== undefined && (
          <div className="flex items-center justify-center gap-4">
            <div className="flex-1 max-w-md bg-slate-200 rounded-full h-2">
              <div 
                className="bg-[#4A3B7A] h-2 rounded-full transition-all duration-500"
                style={{ width: `${status.progress_percentage}%` }}
              ></div>
            </div>
            <span className="text-sm font-medium text-[#4A3B7A]">
              {status.progress_percentage.toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-medium mb-1">Training Failed</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg p-8 shadow-sm space-y-6">
        <div className="space-y-4">
          {getProgressSteps().map((step, index) => (
            <TrainingStep
              key={index}
              label={step.label}
              completed={step.completed}
              current={step.current}
            />
          ))}
        </div>

        {status && (
          <div className="pt-6 border-t border-slate-200 space-y-2 text-sm">
            {status.current_epoch !== undefined && status.total_epochs && (
              <div className="flex justify-between text-slate-600">
                <span>Epoch:</span>
                <span className="text-[#4A3B7A] font-medium">
                  {status.current_epoch} / {status.total_epochs}
                </span>
              </div>
            )}
            {status.current_loss !== undefined && (
              <div className="flex justify-between text-slate-600">
                <span>Current Loss:</span>
                <span className="text-[#4A3B7A] font-mono">
                  {status.current_loss.toFixed(4)}
                </span>
              </div>
            )}
            {status.best_loss !== undefined && (
              <div className="flex justify-between text-slate-600">
                <span>Best Loss:</span>
                <span className="text-green-600 font-mono">
                  {status.best_loss.toFixed(4)}
                </span>
              </div>
            )}
            {status.estimated_time_remaining !== undefined && (
              <div className="flex justify-between text-slate-600">
                <span>Est. Time Remaining:</span>
                <span className="text-[#4A3B7A] font-medium">
                  {formatTime(status.estimated_time_remaining)}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <p className="text-sm text-slate-700">
          🤖 <span className="font-medium">Training in progress...</span> Your mirror bot is learning to play just like you. Feel free to grab a coffee!
        </p>
      </div>
    </div>
  );
}

function TrainingStep({ label, completed, current }: { label: string; completed: boolean; current: boolean }) {
  return (
    <div className="flex items-center gap-4">
      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
        completed ? 'bg-green-500' : current ? 'bg-[#4A3B7A] animate-pulse' : 'bg-slate-200'
      }`}>
        {completed ? (
          <CheckCircle2 className="w-4 h-4 text-white" />
        ) : (
          <div className="w-2 h-2 bg-white rounded-full"></div>
        )}
      </div>
      <span className={`text-sm ${completed || current ? 'text-slate-700' : 'text-slate-400'}`}>
        {label}
      </span>
    </div>
  );
}
