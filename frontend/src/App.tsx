import { useState } from 'react';
import axios from 'axios';
import SummaryDisplay from './SummaryDisplay';
import { APIResponse, ParsedAPIResponse, PaperSummary } from './types';

// Get the API URL from environment variables.
// In development, this will be http://localhost:8000
// In production, we'll set this on Render.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState<string>('');
  const [summaryData, setSummaryData] = useState<ParsedAPIResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setSummaryData(null);

    try {
      const response = await axios.post<APIResponse>(`${API_URL}/summarize`, { url });
      
      if (response.data && response.data.summary) {
        // The Gemini response is a stringified JSON, so we parse it
        const parsedSummary: PaperSummary = JSON.parse(response.data.summary);
        const parsedData: ParsedAPIResponse = { 
          summary: parsedSummary, 
          title: response.data.title 
        };
        setSummaryData(parsedData);
      } else {
        throw new Error('Invalid response structure from server.');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unknown error occurred.';
      setError(`Error: ${errorMessage}`);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Research
            </span>
            LikeIAmFive 🧠💡
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Transform complex research papers into simple, digestible explanations. 
            Just paste an{' '}
            <a 
              href="https://arxiv.org/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 font-medium hover:text-blue-700 underline decoration-2 underline-offset-2"
            >
              arXiv.org
            </a>{' '}
            paper link to get started.
          </p>
        </div>

        {/* Input Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-white/80 backdrop-blur-sm border border-white/20 rounded-3xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="url" className="block text-slate-700 font-semibold mb-3 text-lg">
                  arXiv Paper URL
                </label>
                <input
                  type="url"
                  id="url"
                  name="url"
                  placeholder="e.g., https://arxiv.org/abs/1706.03762"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="w-full px-6 py-4 rounded-2xl border-2 border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all duration-200 bg-white/90 backdrop-blur-sm placeholder:text-slate-400 text-lg"
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold px-8 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/30 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none text-lg"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing Paper...
                  </span>
                ) : (
                  '✨ Explain It Like I\'m Five!'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-8 text-center">
              <div className="flex items-center justify-center gap-4 mb-3">
                <div className="w-6 h-6 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin"></div>
                <p className="font-semibold text-blue-800 text-lg">
                  🔍 Analyzing paper and generating simple explanation...
                </p>
              </div>
              <p className="text-sm text-blue-600 opacity-80">
                This usually takes 30-60 seconds
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl p-8 text-center">
              <div className="flex items-center justify-center gap-3">
                <span className="text-2xl">⚠️</span>
                <p className="font-semibold text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {summaryData && (
          <div className="animate-in slide-in-from-bottom-4 duration-500">
            <SummaryDisplay data={summaryData} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
