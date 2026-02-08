import { useNavigate } from 'react-router';
import { Play, Settings, TrendingUp, Calendar } from 'lucide-react';

export function Dashboard() {
  const navigate = useNavigate();

  const recentGames = [
    { id: 1, date: 'Feb 2, 2026', result: 'Win', similarity: 87, moves: 42 },
    { id: 2, date: 'Feb 1, 2026', result: 'Loss', similarity: 92, moves: 38 },
    { id: 3, date: 'Jan 31, 2026', result: 'Win', similarity: 79, moves: 51 },
    { id: 4, date: 'Jan 30, 2026', result: 'Draw', similarity: 85, moves: 47 },
  ];

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
