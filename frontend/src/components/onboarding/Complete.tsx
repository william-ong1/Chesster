import { useNavigate } from 'react-router';
import { CheckCircle2, Sparkles } from 'lucide-react';

export function Complete() {
  const navigate = useNavigate();

  return (
    <div className="max-w-2xl mx-auto text-center space-y-8 animate-slide-in-right">
      <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto">
        <CheckCircle2 className="w-12 h-12 text-white" />
      </div>

      <div className="space-y-4">
        <h1 className="text-4xl text-[#4A3B7A]">
          You're All Set!
        </h1>
        <p className="text-slate-600 text-lg">
          Your personalized chess bot is ready to play
        </p>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-white rounded-lg p-8 shadow-lg border-2 border-purple-200">
        <div className="flex items-center justify-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg">Your Mirror Bot Profile</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl text-[#4A3B7A] mb-1">47</div>
            <div className="text-sm text-slate-600">Games analyzed</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl text-[#4A3B7A] mb-1">Aggressive</div>
            <div className="text-sm text-slate-600">Play style</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl text-[#4A3B7A] mb-1">75%</div>
            <div className="text-sm text-slate-600">Human-like</div>
          </div>
        </div>

        <div className="space-y-3 text-left bg-white rounded-lg p-6">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-slate-700">
              Learned your aggressive, tactical playing style
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-slate-700">
              Mapped your opening repertoire (Sicilian, Ruy López, and more)
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-slate-700">
              Calibrated to match your timing and decision patterns
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
        <h3 className="text-sm mb-3">What to expect:</h3>
        <ul className="text-sm text-slate-600 space-y-2 text-left list-disc list-inside">
          <li>Your bot will play similarly to you, with your favorite openings</li>
          <li>After each game, you'll receive a Mirror Report showing style similarity</li>
          <li>The more you play, the better the bot adapts to your evolving style</li>
        </ul>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
        <button 
          onClick={() => navigate('/play')}
          className="bg-[#4A3B7A] text-white px-8 py-3 rounded-lg hover:bg-[#3D3066] transition-colors shadow-lg hover:shadow-xl"
        >
          Play Your First Game
        </button>
        <button 
          onClick={() => navigate('/dashboard')}
          className="border-2 border-[#4A3B7A] text-[#4A3B7A] px-8 py-3 rounded-lg hover:bg-purple-50 transition-colors"
        >
          View Dashboard
        </button>
      </div>
    </div>
  );
}
