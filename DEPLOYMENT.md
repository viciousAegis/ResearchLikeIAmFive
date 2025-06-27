# ResearchLikeIAmFive - Unified Deployment Guide

## 🚀 Architecture Overview

This project has been migrated from a separate backend/frontend structure to a unified architecture optimized for Vercel deployment:

- **Frontend**: React + TypeScript + Vite (in `/src`, `/public`)
- **Backend**: Serverless functions (in `/api`)
- **Deployment**: Single Vercel deployment

## 📁 Project Structure

```
project-root/
├── api/                    # Serverless functions
│   ├── summarize.py       # Main paper summarization endpoint
│   ├── health.py          # Health check endpoint
│   ├── _config.py         # Shared configuration
│   ├── _utils.py          # Shared utilities
│   └── _rate_limiter.py   # Rate limiting functionality
├── src/                   # React frontend source
├── public/                # Static assets
├── dist/                  # Build output (generated)
├── package.json           # Frontend dependencies & scripts
├── requirements.txt       # Python dependencies for API
├── vercel.json            # Vercel deployment config
└── vite.config.js         # Vite build configuration
```

## 🛠️ Local Development

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- Vercel CLI (optional): `npm i -g vercel`

### Setup

1. **Install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # Create .env.local file
   echo "GOOGLE_API_KEY=your_google_ai_api_key" > .env.local
   ```

4. **Run development server:**
   ```bash
   # Frontend only
   npm run dev
   
   # Full stack with Vercel CLI (recommended)
   vercel dev
   ```

## 🚀 Deployment to Vercel

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Option 2: GitHub Integration

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Migrate to unified architecture"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Add environment variable: `GOOGLE_API_KEY`
   - Deploy!

## 🔧 Environment Variables

Set these in Vercel dashboard or `.env.local`:

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI Studio API key | ✅ Yes |

## 📋 API Endpoints

- `GET /api/health` - Health check
- `POST /api/summarize` - Paper summarization

### Example API Usage:

```javascript
// Health check
fetch('/api/health')

// Summarize paper
fetch('/api/summarize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://arxiv.org/abs/2301.00001',
    explanation_style: 'five-year-old'
  })
})
```

## 🏗️ Build Process

The build process is handled automatically by Vercel:

1. **Frontend**: Vite builds React app to `/dist`
2. **Backend**: Python functions in `/api` are deployed as serverless functions
3. **Routing**: `vercel.json` configures API routes and SPA fallback

## 🔍 Troubleshooting

### Common Issues:

1. **API functions timeout:**
   - Check function execution time in Vercel dashboard
   - Optimize paper processing for shorter execution

2. **Cold starts:**
   - First request might be slow
   - Subsequent requests will be faster

3. **Environment variables:**
   - Ensure `GOOGLE_API_KEY` is set in Vercel
   - Check Vercel dashboard → Settings → Environment Variables

4. **Build failures:**
   - Check Vercel build logs
   - Ensure all dependencies are in `package.json` and `requirements.txt`

## 📊 Performance Considerations

- **Serverless limitations**: 30s execution limit (Hobby plan)
- **PDF processing**: Limited to 10MB files for serverless
- **Memory**: 1GB limit per function
- **Cold starts**: ~2-3s for Python functions

## 🔄 Migration Notes

This project was migrated from:
- **Before**: Separate FastAPI backend + React frontend
- **After**: Unified Vercel deployment with serverless functions

Key changes:
- FastAPI routes → Vercel serverless functions
- Separate deployments → Single Vercel deployment  
- Docker/server → Serverless functions
- Rate limiting → Vercel built-in limits

## 🆘 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify environment variables
3. Test API functions individually
4. Check this README for troubleshooting steps
