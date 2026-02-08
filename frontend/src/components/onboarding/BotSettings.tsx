import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Settings, ArrowRight } from 'lucide-react';

export function BotSettings() {
  const navigate = useNavigate();
  const [mimicStrength, setMimicStrength] = useState(75);

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-slide-in-right">
      <div className="text-center space-y-4">
        <div className="w-20 h-20 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto">
          <Settings className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl text-[#4A3B7A]">
          Configure Your Bot
        </h1>
        <p className="text-slate-600">
          Customize how your mirror plays
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-8 shadow-sm space-y-8">
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm tracking-wide text-purple-800">
              MIMIC STRENGTH
            </h2>
            <span className="text-sm px-3 py-1 bg-purple-100 text-[#4A3B7A] rounded-full">
              {mimicStrength}% Human-like
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={mimicStrength}
            onChange={(e) => setMimicStrength(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#4A3B7A]"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>More accurate</span>
            <span>More human-like</span>
          </div>
          <p className="text-sm text-slate-600 mt-4">
            The bot will make occasional human-like mistakes to feel more natural.
            Higher values = more personality, more blunders.
          </p>
        </div>

        <div className="border-t border-slate-200 pt-8">
          <h2 className="text-sm tracking-wide text-purple-800 mb-4">
            STYLE SETTINGS
          </h2>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-4 border-2 border-slate-200 rounded-lg hover:border-purple-300 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4 accent-[#4A3B7A]" />
              <div className="flex-1">
                <div className="text-sm">Match my opening repertoire</div>
                <div className="text-xs text-slate-500">
                  Bot will play your preferred openings
                </div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-4 border-2 border-slate-200 rounded-lg hover:border-purple-300 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4 accent-[#4A3B7A]" />
              <div className="flex-1">
                <div className="text-sm">Mirror my time management</div>
                <div className="text-xs text-slate-500">
                  Think at a similar pace
                </div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-4 border-2 border-slate-200 rounded-lg hover:border-purple-300 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-[#4A3B7A]" />
              <div className="flex-1">
                <div className="text-sm">Show hints</div>
                <div className="text-xs text-slate-500">
                  Get move suggestions when stuck
                </div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <p className="text-sm text-slate-700">
          ⚙️ You can adjust these settings anytime from your profile page.
        </p>
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => navigate('/training')}
          className="bg-[#4A3B7A] text-white px-8 py-3 rounded-lg hover:bg-[#3D3066] transition-colors flex items-center gap-2"
        >
          Complete Setup
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}