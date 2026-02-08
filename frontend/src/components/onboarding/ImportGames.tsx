import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { uploadAPI } from '../../services/api';

export function ImportGames() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await uploadAPI.uploadPGN(file);
      if (response.data.success) {
        navigate('/analyzing');
      } else {
        setError(response.data.message || 'Failed to upload PGN file');
        setUploading(false);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to upload file. Please try again.');
      setUploading(false);
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
        
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
        
        <label className="block">
          <div className={`border-2 border-dashed border-slate-300 rounded-lg p-12 text-center transition-colors ${
            uploading ? 'opacity-50 cursor-not-allowed' : 'hover:border-[#4A3B7A] cursor-pointer'
          }`}>
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-700 mb-2">
              {uploading ? 'Uploading...' : 'Drop your PGN file here or click to browse'}
            </p>
            <p className="text-sm text-slate-500">
              Supports .pgn files up to 10MB
            </p>
            <input
              type="file"
              accept=".pgn"
              onChange={handleFileUpload}
              disabled={uploading}
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
