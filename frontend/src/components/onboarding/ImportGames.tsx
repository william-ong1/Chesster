import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Upload, FileText } from 'lucide-react';

export function ImportGames() {
  const navigate = useNavigate();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Simulate file processing
      setTimeout(() => navigate('/analyzing'), 800);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-slide-in-right">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-[#4A3B7A] rounded-full flex items-center justify-center mx-auto">
          <Upload className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl text-[#4A3B7A]">
          Import Your Games
        </h1>
        <p className="text-slate-600 text-lg">
          We'll analyze your play style and build your personalized chess bot.
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-8 h-1 bg-[#4A3B7A] rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
          <div className="w-8 h-1 bg-slate-300 rounded"></div>
        </div>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-sm border-2 border-[#4A3B7A]">
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-6 h-6 text-[#4A3B7A]" />
          <h3 className="text-lg">Upload PGN File</h3>
        </div>
        <label className="block">
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center hover:border-[#4A3B7A] transition-colors cursor-pointer">
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-700 mb-2">
              Drop your PGN file here or click to browse
            </p>
            <p className="text-sm text-slate-500">
              Supports .pgn files up to 10MB
            </p>
            <input
              type="file"
              accept=".pgn"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </label>
        <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
          <p className="text-sm text-slate-700">
            💡 <span className="font-medium">How to get your games:</span> Export your game history from Chess.com or Lichess as a PGN file. The more games you upload, the more accurate your bot will be.
          </p>
        </div>
      </div>
    </div>
  );
}
