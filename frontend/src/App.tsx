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
    <main className="container">
      <header className="container">
        <h1>ResearchLikeIAmFive 🧠💡</h1>
        <p>Paste an <a href="https://arxiv.org/" target="_blank" rel="noopener noreferrer">arXiv.org</a> paper link to get a simple explanation.</p>
      </header>

      <form onSubmit={handleSubmit}>
        <label htmlFor="url">arXiv Paper URL</label>
        <input
          type="url"
          id="url"
          name="url"
          placeholder="e.g., https://arxiv.org/abs/1706.03762"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Explain It!'}
        </button>
      </form>

      {isLoading && <article aria-busy="true">Summarizing... please wait a moment.</article>}
      {error && <article style={{ color: 'var(--pico-color-red-500)' }}>{error}</article>}
      {summaryData && <SummaryDisplay data={summaryData} />}
    </main>
  );
}

export default App;
