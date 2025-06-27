# Local Development Guide

## 🛠️ Development Setup Complete!

Your ResearchLikeIAmFive application is now ready for local development with both frontend and API functions working together.

## 🚀 Running the Application

### For Full Development (Frontend + API):
```bash
vercel dev
```
This starts both:
- Frontend at `http://localhost:3000`
- API functions at `http://localhost:3000/api/*`

### For Frontend Only:
```bash
npm run dev
```
This starts only the React frontend (API calls will fail since serverless functions won't be available).

## 📡 Available Endpoints

When running `vercel dev`, you can test:

- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:3000/api/health
- **Summarize**: POST to http://localhost:3000/api/summarize

## 🧪 Testing the API

Test the health endpoint:
```bash
curl http://localhost:3000/api/health
```

Test the summarize endpoint:
```bash
curl -X POST http://localhost:3000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/1706.03762", "explanation_style": "five-year-old"}'
```

## 🔧 Development Commands

- `vercel dev` - Full app with API functions
- `npm run dev` - Frontend only
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `python test_api.py` - Test API functions

## 🌟 Next Steps

1. ✅ Local development working
2. ✅ API functions operational
3. ✅ Rate limiting implemented
4. Ready to deploy: `vercel --prod`

Your unified application is now fully functional in development mode! 🎉
