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
  const [hasInteracted, setHasInteracted] = useState<boolean>(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setHasInteracted(true);
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
          title: response.data.title,
          figures: response.data.figures || []
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
    <div className="min-h-screen bg-white">
      {/* Hero Section - Apple Style Full Screen */}
      <div className="bg-gradient-to-br from-gray-900 via-black to-gray-800 min-h-screen flex flex-col">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          {/* Navigation Bar */}
          <nav className="max-w-7xl mx-auto flex items-center justify-between mb-8">
            {/* Left side - can be empty for balance */}
            <div className="w-48"></div>
            
            {/* Center - Logo and Title */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">🧠</span>
              </div>
              <span className="text-white font-bold text-xl">Research Like I'm Five</span>
            </div>
            
            {/* Right side - empty for balance */}
            <div className="w-48"></div>
          </nav>

          {/* Hero Content - Full Screen Centered */}
          <div className="flex-1 flex flex-col justify-center text-center max-w-6xl mx-auto">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-tight mb-6">
              Make Research
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Accessible
              </span>
            </h1>
            
            <p className="text-xl text-gray-300 leading-relaxed mb-8 max-w-3xl mx-auto">
              Transform complex research papers into simple explanations that anyone can understand. 
              Just paste an{' '}
              <a 
                href="https://arxiv.org/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 font-semibold hover:text-blue-300 underline decoration-2 underline-offset-2 transition-colors"
              >
                arXiv.org
              </a>{' '}
              paper link to get started.
            </p>
            
            <div className="flex items-center justify-center gap-2 mb-12">
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
                <span className="text-green-400">🌟</span>
                <span className="text-white text-sm font-medium">100% Open Source</span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-300 text-sm">Built with ❤️ for the community</span>
              </div>
            </div>

            {/* Input Form - Centered in Full Screen */}
            <div className="w-full max-w-3xl mx-auto mb-6 px-4">
              <div className="bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 p-6 shadow-2xl">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <input
                      type="url"
                      id="url"
                      name="url"
                      placeholder="https://arxiv.org/abs/1706.03762"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      onFocus={() => setHasInteracted(true)}
                      required
                      className="w-full px-6 py-4 rounded-2xl border-0 bg-white/20 backdrop-blur-sm placeholder:text-gray-300 text-white text-lg outline-none focus:ring-4 focus:ring-blue-500/30 transition-all duration-200"
                    />
                  </div>
                  <button 
                    type="submit" 
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-6 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/30 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none text-lg"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-3">
                        <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Analyzing Paper...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-3">
                        <span className="text-xl">✨</span>
                        Explain It Like I'm Five!
                      </span>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Quick Examples */}
            <div className="text-center">
              <p className="text-gray-300 mb-2 text-sm">Try these popular papers:</p>
              <div className="flex flex-wrap justify-center gap-3">
                {[
                  { title: "Attention Is All You Need", url: "https://arxiv.org/abs/1706.03762" },
                  { title: "GPT-3", url: "https://arxiv.org/abs/2005.14165" },
                  { title: "BERT", url: "https://arxiv.org/abs/1810.04805" }
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setUrl(example.url)}
                    className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white text-sm hover:bg-white/20 transition-all duration-200 border border-white/20"
                  >
                    {example.title}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Demo/Preview Section - Shows before user interaction */}
      {!hasInteracted && !summaryData && (
        <div className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                See it in
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  {" "}action
                </span>
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Here's how we transform complex research into simple explanations
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="text-center transform transition-all duration-300 hover:scale-105">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl text-white">📄</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">1. Paste Link</h3>
                <p className="text-gray-600 leading-relaxed">
                  Simply paste any arXiv paper URL and we'll fetch the research for you
                </p>
              </div>

              {/* Step 2 */}
              <div className="text-center transform transition-all duration-300 hover:scale-105">
                <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl text-white">🧠</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">2. AI Analysis</h3>
                <p className="text-gray-600 leading-relaxed">
                  Our AI reads the entire paper and extracts key insights and figures
                </p>
              </div>

              {/* Step 3 */}
              <div className="text-center transform transition-all duration-300 hover:scale-105">
                <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl text-white">✨</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">3. Simple Explanation</h3>
                <p className="text-gray-600 leading-relaxed">
                  Get clear explanations with visual insights that anyone can understand
                </p>
              </div>
            </div>

            {/* Example Preview */}
            <div className="mt-16 bg-white rounded-3xl shadow-2xl p-8 max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Example: Attention Is All You Need</h3>
                <p className="text-gray-600">The paper that introduced the Transformer architecture</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-3">🎯 The Gist</h4>
                  <p className="text-gray-700 leading-relaxed">
                    "This paper introduces a new way for computers to understand language by paying attention to different parts of sentences, like how you focus on different words when reading."
                  </p>
                </div>
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-3">💡 The Big Idea</h4>
                  <p className="text-gray-700 leading-relaxed">
                    "Think of it like a spotlight that can shine on multiple words at once, helping the computer understand which words are most important for understanding meaning."
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State - Apple Style */}
      {isLoading && (
        <div className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="bg-white rounded-3xl shadow-2xl p-12">
              <div className="flex items-center justify-center gap-6 mb-8">
                <div className="w-12 h-12 border-4 border-blue-600/30 border-t-blue-600 rounded-full animate-spin"></div>
                <div className="text-left">
                  <p className="font-bold text-blue-800 text-2xl mb-2">
                    🔍 Analyzing paper...
                  </p>
                  <p className="text-blue-600 text-lg">
                    Extracting insights and generating explanations
                  </p>
                </div>
              </div>
              <p className="text-gray-600">
                This usually takes 30-60 seconds
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error State - Apple Style */}
      {error && (
        <div className="py-20 bg-gradient-to-br from-red-50 to-pink-50">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="bg-white rounded-3xl shadow-2xl p-12">
              <div className="flex items-center justify-center gap-4 mb-6">
                <span className="text-4xl">⚠️</span>
                <div>
                  <p className="font-bold text-red-800 text-xl">Something went wrong</p>
                  <p className="text-red-600">{error}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {summaryData && (
        <div className="animate-in slide-in-from-bottom-4 duration-700">
          <SummaryDisplay data={summaryData} />
        </div>
      )}

      {/* Sticky GitHub CTA */}
      <div className="fixed bottom-6 left-6 z-40">
        <div className="bg-gray-900/90 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-700/50 px-6 py-4 transform transition-all duration-300 hover:scale-105 hover:shadow-2xl">
          <a
            href="https://github.com/akshitsinha3/ResearchLikeIAmFive"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-4 text-white group"
          >
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold group-hover:text-blue-200 transition-colors">⭐ Star on GitHub</p>
              <p className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors">Help us grow!</p>
            </div>
          </a>
        </div>
      </div>

      {/* Floating Sticky Footer - Creator Credit */}
      <div className="fixed bottom-6 right-6 z-40">
        <div className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 px-6 py-4 transform transition-all duration-300 hover:scale-105 hover:shadow-2xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <span className="text-white text-lg font-bold">A</span>
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold text-gray-900">Created by</p>
              <a 
                href="https://github.com/akshitsinha3" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Akshit Sinha
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
