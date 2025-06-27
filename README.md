# Research Like I'm Five - Enhanced with Figures

A beautiful, Apple-inspired web application that transforms complex research papers into simple explanations with visual insights.

## Features

### 🎨 Apple-Inspired Design
- Clean, modern interface inspired by Apple's demo day presentations
- Smooth animations and transitions
- Glass morphism effects and gradient backgrounds
- Responsive design that works on all devices

### 🖼️ Figure Integration
- Automatic extraction of figures from research papers
- AI-powered figure descriptions and importance explanations
- Interactive figure viewer with full-screen modal
- Fallback handling for figures that can't be displayed

### 🧠 AI-Powered Explanations
- Simple summaries of complex research
- Real-world analogies to explain difficult concepts
- Key findings and terminology explanations
- Experimental details breakdown

## Technology Stack

### Backend
- **FastAPI** - High-performance web framework
- **Google Gemini AI** - Advanced language model for explanations
- **PyMuPDF** - PDF processing and figure extraction
- **arXiv API** - Research paper fetching

### Frontend
- **React + TypeScript** - Modern web development
- **Vite** - Fast development and building
- **Tailwind CSS** - Utility-first styling
- **Custom animations** - Apple-inspired interactions

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- Google Gemini API key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   uv install
   ```

3. Create a `.env` file with your Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. Start the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:5173`

## How to Use

1. Copy any arXiv paper URL (e.g., `https://arxiv.org/abs/1706.03762`)
2. Paste it into the input field
3. Click "Explain It Like I'm Five!"
4. Enjoy the simplified explanation with visual insights
5. Click on any figure to view it in full screen

## Design Philosophy

This application follows Apple's design principles:

- **Simplicity** - Clean, uncluttered interface
- **Clarity** - Clear typography and visual hierarchy
- **Delight** - Smooth animations and interactions
- **Accessibility** - Keyboard navigation and screen reader support

## Figure Processing

The application automatically:
1. Extracts images from research papers
2. Filters out decorative elements (logos, headers, etc.)
3. Converts images to web-compatible formats
4. Generates AI descriptions for each figure
5. Explains why each figure is important

## API Endpoints

- `GET /` - Health check
- `POST /summarize` - Process arXiv paper and return explanation with figures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- OpenAI for inspiration on AI-powered explanations
- Apple for design inspiration
- arXiv for providing open access to research papers
- Google for the Gemini AI API
