import { useNavigate } from 'react-router';

export function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="text-center space-y-8 animate-fade-in">
      <div className="space-y-4">
        <div className="inline-block px-4 py-1.5 bg-purple-100 text-purple-800 rounded-full text-sm tracking-wide">
          NOW IN BETA
        </div>
        <h1 className="text-5xl text-[#4A3B7A] max-w-2xl mx-auto leading-tight">
          Play against a bot <br />
          <span className="text-black">that learns your style.</span>
        </h1>
        <p className="text-slate-600 text-lg max-w-xl mx-auto">
          Chesster analyzes your games and builds an opponent that thinks,
          blunders, and plays exactly like you.
        </p>
      </div>

      <button
        onClick={() => navigate('/import')}
        className="bg-[#4A3B7A] text-white px-8 py-3 rounded-lg hover:bg-[#3D3066] transition-colors text-lg shadow-lg hover:shadow-xl"
      >
        Get Started
      </button>

      <div className="pt-12 border-t border-slate-200 mt-16">
        <h2 className="text-sm tracking-wide text-purple-800 mb-8">
          WHAT CHESSTER DOES
        </h2>
        
        <div className="grid md:grid-cols-2 gap-6 text-left">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-start gap-4">
              <div className="w-2 h-2 bg-[#4A3B7A] rounded-full mt-2"></div>
              <div>
                <h3 className="text-black mb-2">Learns your style</h3>
                <p className="text-slate-600 text-sm">
                  Analyzes openings, tendencies, and decision patterns from your game history.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-start gap-4">
              <div className="w-2 h-2 bg-[#4A3B7A] rounded-full mt-2"></div>
              <div>
                <h3 className="text-black mb-2">Mirror matches</h3>
                <p className="text-slate-600 text-sm">
                  Face a bot that mimics your strengths — and your weaknesses.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-start gap-4">
              <div className="w-2 h-2 bg-[#4A3B7A] rounded-full mt-2"></div>
              <div>
                <h3 className="text-black mb-2">Style reports</h3>
                <p className="text-slate-600 text-sm">
                  After every game, see exactly how closely the bot matched your play.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 p-6 rounded-lg border-2 border-purple-200">
            <div className="flex items-start gap-4">
              <div className="w-2 h-2 bg-[#4A3B7A] rounded-full mt-2"></div>
              <div>
                <h3 className="text-black mb-2">Import games</h3>
                <p className="text-slate-600 text-sm">
                  Upload your PGN history and we build your style profile instantly.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-12">
        <h2 className="text-sm tracking-wide text-purple-800 mb-8">
          HOW IT WORKS
        </h2>
        
        <div className="space-y-6">
          <div className="flex items-start gap-4 bg-white p-6 rounded-lg shadow-sm">
            <div className="w-10 h-10 bg-[#4A3B7A] text-white rounded-lg flex items-center justify-center flex-shrink-0">
              1
            </div>
            <div className="text-left">
              <h3 className="text-black mb-1">Import your PGN history</h3>
              <p className="text-slate-600 text-sm">
                Upload game files from Chess.com or Lichess. We parse your style automatically.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 bg-white p-6 rounded-lg shadow-sm">
            <div className="w-10 h-10 bg-[#4A3B7A] text-white rounded-lg flex items-center justify-center flex-shrink-0">
              2
            </div>
            <div className="text-left">
              <h3 className="text-black mb-1">Meet your mirror</h3>
              <p className="text-slate-600 text-sm">
                The bot learns your openings, timing, and tendencies.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 bg-white p-6 rounded-lg shadow-sm">
            <div className="w-10 h-10 bg-[#4A3B7A] text-white rounded-lg flex items-center justify-center flex-shrink-0">
              3
            </div>
            <div className="text-left">
              <h3 className="text-black mb-1">Play & compare</h3>
              <p className="text-slate-600 text-sm">
                A Mirror Report after each game shows your style similarity score.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
