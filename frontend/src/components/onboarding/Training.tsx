import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Sparkles, CheckCircle2 } from 'lucide-react';

export function Training() {
  const navigate = useNavigate();

  useEffect(() => {
    // Simulate training completion
    const timer = setTimeout(() => {
      navigate('/complete');
    }, 3500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="max-w-2xl mx-auto text-center space-y-8 py-16 animate-slide-in-right">
      <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto animate-pulse">
        <Sparkles className="w-10 h-10 text-white" />
      </div>

      <div className="space-y-4">
        <h1 className="text-4xl text-[#4A3B7A]">
          Training Your Bot
        </h1>
        <p className="text-slate-600 text-lg">
          Building your personalized chess opponent...
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded animate-pulse"></div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-8 shadow-sm space-y-6">
        <div className="space-y-4">
          <TrainingStep 
            label="Calibrating opening repertoire"
            completed={true}
            current={false}
          />
          <TrainingStep 
            label="Learning tactical preferences"
            completed={true}
            current={false}
          />
          <TrainingStep 
            label="Adjusting mimic strength"
            completed={false}
            current={true}
          />
          <TrainingStep 
            label="Fine-tuning playing style"
            completed={false}
            current={false}
          />
          <TrainingStep 
            label="Finalizing bot parameters"
            completed={false}
            current={false}
          />
        </div>

        <div className="pt-6 border-t border-slate-200">
          <div className="text-sm text-slate-600">
            Training with <span className="text-[#4A3B7A]">47 games</span> and your preferences
          </div>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <p className="text-sm text-slate-700">
          🤖 <span className="font-medium">Almost there!</span> Your mirror bot is learning to play just like you. This should only take a moment.
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
