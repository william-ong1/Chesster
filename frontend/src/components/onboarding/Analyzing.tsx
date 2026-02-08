import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Brain, CheckCircle2 } from 'lucide-react';

export function Analyzing() {
  const navigate = useNavigate();

  useEffect(() => {
    // Simulate analysis completion
    const timer = setTimeout(() => {
      navigate('/profile');
    }, 3500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="max-w-2xl mx-auto text-center space-y-8 py-16 animate-slide-in-right">
      <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto animate-pulse">
        <Brain className="w-10 h-10 text-white" />
      </div>

      <div className="space-y-4">
        <h1 className="text-4xl text-[#4A3B7A]">
          Analyzing Your Games
        </h1>
        <p className="text-slate-600 text-lg">
          Building your unique chess profile...
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-8 shadow-sm space-y-6">
        <div className="space-y-4">
          <AnalysisStep 
            label="Parsing game files"
            completed={true}
            current={false}
          />
          <AnalysisStep 
            label="Analyzing opening repertoire"
            completed={true}
            current={false}
          />
          <AnalysisStep 
            label="Identifying tactical patterns"
            completed={false}
            current={true}
          />
          <AnalysisStep 
            label="Calculating playing tendencies"
            completed={false}
            current={false}
          />
          <AnalysisStep 
            label="Building mirror profile"
            completed={false}
            current={false}
          />
        </div>

        <div className="pt-6 border-t border-slate-200">
          <div className="text-sm text-slate-600">
            <span className="text-[#4A3B7A]">47 games</span> found and being analyzed
          </div>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <p className="text-sm text-slate-700">
          💡 <span className="font-medium">Pro tip:</span> The more games we analyze, the more accurate your bot will be. You can always import more games later.
        </p>
      </div>
    </div>
  );
}

function AnalysisStep({ label, completed, current }: { label: string; completed: boolean; current: boolean }) {
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
