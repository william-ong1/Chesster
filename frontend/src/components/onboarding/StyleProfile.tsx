import { useNavigate } from 'react-router';
import { User, ArrowRight } from 'lucide-react';

export function StyleProfile() {
  const navigate = useNavigate();

  const openings = [
    { name: 'Sicilian Defense', percentage: 38 },
    { name: 'Ruy López', percentage: 25 },
    { name: "King's Indian", percentage: 18 },
    { name: 'French Defense', percentage: 12 },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-slide-in-right">
      <div className="text-center space-y-4">
        <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto">
          <User className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl text-[#4A3B7A]">
          Your Style Profile
        </h1>
        <p className="text-slate-600">
          Built from <span className="text-[#4A3B7A]">47 imported games</span>
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-8 shadow-sm space-y-8">
        <div>
          <h2 className="text-sm tracking-wide text-purple-800 mb-4">
            PLAYING STYLE
          </h2>
          <div className="flex gap-3 flex-wrap">
            <span className="px-4 py-2 border-2 border-[#4A3B7A] text-[#4A3B7A] rounded-lg">
              Aggressive
            </span>
            <span className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg">
              Tactical
            </span>
            <span className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg">
              Central Control
            </span>
          </div>
          <p className="text-slate-600 mt-4">
            You favor sharp, attacking lines with early piece development. You're comfortable
            sacrificing material for positional advantages.
          </p>
        </div>

        <div className="border-t border-slate-200 pt-8">
          <h2 className="text-sm tracking-wide text-purple-800 mb-4">
            PREFERRED OPENINGS
          </h2>
          <div className="space-y-3">
            {openings.map((opening) => (
              <div key={opening.name}>
                <div className="flex justify-between mb-1.5">
                  <span className="text-sm">{opening.name}</span>
                  <span className="text-sm text-slate-500">{opening.percentage}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#4A3B7A] rounded-full transition-all"
                    style={{ width: `${opening.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-200 pt-8">
          <h2 className="text-sm tracking-wide text-purple-800 mb-4">
            KEY INSIGHTS
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl text-[#4A3B7A] mb-1">62%</div>
              <div className="text-sm text-slate-600">Win rate as White</div>
            </div>
            <div className="text-center">
              <div className="text-3xl text-[#4A3B7A] mb-1">18.5</div>
              <div className="text-sm text-slate-600">Avg move speed (sec)</div>
            </div>
            <div className="text-center">
              <div className="text-3xl text-[#4A3B7A] mb-1">High</div>
              <div className="text-sm text-slate-600">Tactical awareness</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <h3 className="text-sm mb-2">What happens next?</h3>
        <p className="text-sm text-slate-700">
          We'll configure your mirror bot to match these patterns. You can adjust
          mimic strength on the next screen.
        </p>
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => navigate('/settings')}
          className="bg-[#4A3B7A] text-white px-8 py-3 rounded-lg hover:bg-[#3D3066] transition-colors flex items-center gap-2"
        >
          Configure Bot Settings
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
