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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-16 max-w-5xl mx-auto">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-lg mb-6">
            <span className="text-3xl">🧠</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 text-gray-900">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Research
            </span>
            <span className="text-gray-800"> Like I'm Five</span>
          </h1>
          <p className="text-xl text-gray-600 leading-relaxed mb-8">
            Transform complex research papers into simple, digestible explanations that anyone can understand. 
            Just paste an{' '}
            <a 
              href="https://arxiv.org/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 font-semibold hover:text-blue-700 underline decoration-2 underline-offset-2 transition-colors"
            >
              arXiv.org
            </a>{' '}
            paper link to get started.
          </p>
        </div>

        {/* Input Form */}
        <div className="max-w-3xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 transition-all duration-300 hover:shadow-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="url" className="block text-gray-800 font-semibold mb-3 text-lg">
                  📄 arXiv Paper URL
                </label>
                <input
                  type="url"
                  id="url"
                  name="url"
                  placeholder="e.g., https://arxiv.org/abs/1706.03762"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="w-full px-6 py-4 rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all duration-200 bg-white placeholder:text-gray-400 text-lg outline-none"
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/30 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none text-lg"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing Paper...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    ✨ Explain It Like I'm Five!
                  </span>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="max-w-3xl mx-auto mb-12">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="w-8 h-8 border-3 border-blue-600/30 border-t-blue-600 rounded-full animate-spin"></div>
                <p className="font-semibold text-blue-800 text-xl">
                  🔍 Analyzing paper and generating simple explanation...
                </p>
              </div>
              <p className="text-blue-600">
                This usually takes 30-60 seconds
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="max-w-3xl mx-auto mb-12">
            <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                <span className="text-3xl">⚠️</span>
                <p className="font-semibold text-red-800 text-lg">Something went wrong</p>
              </div>
              <p className="text-red-700">{error}</p>
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
