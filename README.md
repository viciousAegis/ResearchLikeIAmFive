# 🧠 Research Like I'm Five

*"If you can't explain it simply, you don't understand it well enough."* — Albert Einstein

Transform complex research p## 📱 How to Use

1. Copy any arXiv paper URL (e.g., `https://arxiv.org/abs/1706.03762`)
2. Paste it into the input field  
3. Choose your explanation style
4. Click "Explain It Like I'm Five!"
5. Enjoy the simplified explanation

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite (builds to `/dist`)
- **Backend**: Serverless functions in `/api`
- **Deployment**: Single Vercel deployment
- **APIs**: `/api/summarize` and `/api/health`

## 🛠️ Technology Stack

### 🌐 **Unified Serverless Architecture**
- **[Vercel](https://vercel.com/)** - Serverless deployment platform with global CDN
- **[Vercel Functions](https://vercel.com/docs/functions)** - Python serverless functions

### 🐍 **Backend (Serverless)**
- **[Google Gemini AI](https://ai.google.dev/)** - State-of-the-art language model for intelligent explanations
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - Professional PDF processing and figure extraction
- **[arXiv API](https://info.arxiv.org/help/api/)** - Direct access to the world's largest repository of research papers
- **[Pydantic](https://pydantic.dev/)** - Data validation with Python type hints

### ⚛️ **Frontend**
- **[React 19](https://react.dev/)** - Latest React with concurrent features
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript for robust development
- **[Vite](https://vite.dev/)** - Next-generation frontend tooling with instant hot reload
- **[Tailwind CSS 4](https://tailwindcss.com/)** - Utility-first CSS framework with modern features
- **[Lucide React](https://lucide.dev/)** - Beautiful, customizable SVG icons
- **[Axios](https://axios-http.com/)** - Promise-based HTTP client for seamless API communication easy-to-understand explanations with the power of AI and stunning visual design.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg)](https://reactjs.org/)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000.svg)](https://vercel.com/)

## ✨ What is Research Like I'm Five?

**Research Like I'm Five** is a revolutionary web application that bridges the gap between complex academic research and public understanding. Simply paste an arXiv paper URL, choose your explanation style, and watch as cutting-edge AI transforms dense scientific jargon into engaging, accessible content.

**🆕 Now with unified architecture!** This application has been optimized for seamless deployment on Vercel with serverless functions, providing lightning-fast performance and global scalability.

### 🎯 Perfect For:
- **Students** who want to understand research papers quickly
- **Educators** looking for engaging ways to explain complex concepts  
- **Professionals** staying up-to-date with research outside their field
- **Curious minds** who love learning but hate academic jargon
- **Anyone** who believes science should be accessible to everyone

## 🚀 Features

### 🎨 **Apple-Inspired Design**
- **Sleek Interface**: Clean, modern design inspired by Apple's presentation aesthetics
- **Smooth Animations**: Delightful micro-interactions and seamless transitions
- **Glass Morphism**: Beautiful frosted glass effects and gradient backgrounds
- **Responsive Design**: Perfect experience on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme switching based on system preferences

### 🖼️ **Advanced Figure Processing**
- **Smart Extraction**: Automatically extracts meaningful figures from PDFs
- **AI Descriptions**: Get intelligent explanations of what each figure shows
- **Interactive Viewer**: Full-screen modal with zoom and navigation
- **Quality Filtering**: Automatically filters out logos, headers, and decorative elements
- **Fallback Handling**: Graceful handling when figures can't be displayed

### � **12 Unique Explanation Styles**
Choose how you want complex research explained:

| Style | Description | Perfect For |
|-------|-------------|-------------|
| 🧸 **Five-Year-Old** | Simple language, everyday analogies | First-time learners |
| 🔥 **Pop Culture** | TikTok vibes, celebrity references, Gen Z slang | Social media natives |
| 🌟 **Anime** | Otaku explanations with power levels and jutsu | Anime enthusiasts |
| 🏆 **Sports** | ESPN-style commentary, championship metaphors | Sports fans |
| 👨‍🍳 **Food** | Gordon Ramsay meets molecular gastronomy | Foodies and chefs |
| 🎮 **Gaming** | Twitch streamer explanations, RPG analogies | Gamers |
| 💥 **Marvel** | Superhero analogies, MCU references | Comic book fans |
| ⚡ **Harry Potter** | Hogwarts-style magical explanations | Fantasy lovers |
| 💀 **Brain Rot** | Peak Gen Alpha humor with maximum rizz | Meme connoisseurs |
| 🔴 **Reddit** | Classic Reddit commentary and memes | Reddit users |
| 🎭 **Shakespearean** | Elizabethan English, iambic pentameter | Literature enthusiasts |

### 🧠 **AI-Powered Analysis**
- **One-Line Gist**: The entire paper in one compelling sentence
- **Perfect Analogies**: Complex concepts explained through familiar metaphors
- **Experimental Breakdown**: Clear explanation of research methodology
- **Key Findings**: 3-5 bullet points of the most important discoveries
- **Real-World Impact**: Why this research matters for everyday life
- **Technical Terms**: Simplified definitions of important jargon

## 🛠️ Technology Stack

### 🐍 **Backend**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Lightning-fast, modern web framework with automatic API documentation
- **[Google Gemini AI](https://ai.google.dev/)** - State-of-the-art language model for intelligent explanations
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - Professional PDF processing and figure extraction
- **[arXiv API](https://info.arxiv.org/help/api/)** - Direct access to the world's largest repository of research papers
- **[Pydantic](https://pydantic.dev/)** - Data validation with Python type hints
- **[uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server

### ⚛️ **Frontend**
- **[React 19](https://react.dev/)** - Latest React with concurrent features and server components
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript for robust development
- **[Vite](https://vite.dev/)** - Next-generation frontend tooling with instant hot reload
- **[Tailwind CSS 4](https://tailwindcss.com/)** - Utility-first CSS framework with modern features
- **[Lucide React](https://lucide.dev/)** - Beautiful, customizable SVG icons
- **[Axios](https://axios-http.com/)** - Promise-based HTTP client for seamless API communication

##  🚀 Quick Start

### 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.9+** ([Download here](https://www.python.org/downloads/))
- **Node.js 18+** ([Download here](https://nodejs.org/))
- **Google Gemini API Key** ([Get yours here](https://ai.google.dev/))

### ⚡ Unified Architecture Setup

This application now uses a unified architecture optimized for Vercel deployment:

```bash
# Clone the repository
git clone https://github.com/yourusername/ResearchLikeIAmFive.git
cd ResearchLikeIAmFive

# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment
echo "GOOGLE_API_KEY=your_google_ai_api_key" > .env.local

# Development (with Vercel CLI - recommended)
npm install -g vercel
vercel dev

# Or frontend only
npm run dev
```

### 🌐 Deploy to Vercel

**Option 1: Vercel CLI**
```bash
vercel --prod
```

**Option 2: GitHub Integration**
1. Push to GitHub
2. Connect to Vercel
3. Add `GOOGLE_API_KEY` environment variable
4. Deploy! 🚀

📖 **Need detailed setup instructions?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment guide.

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
4. Enjoy the simplified explanation

## Design Philosophy

This application follows modern design principles:

- **Simplicity** - Clean, uncluttered interface
- **Clarity** - Clear typography and visual hierarchy
- **Delight** - Smooth animations and interactions
- **Accessibility** - Keyboard navigation and screen reader support

## API Endpoints

- `GET /` - Health check
- `POST /summarize` - Process arXiv paper and return explanation

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
- arXiv for providing open access to research papers
- Google for the Gemini AI API
