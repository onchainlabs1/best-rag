# Free Deployment Guide

Complete guide to deploy this RAG + Agent Knowledge Base system online for free.

## 🎯 Recommended Free Stack

### Best Option (Recommended)
- **Frontend**: Vercel (Next.js optimized, free tier)
- **Backend**: Render or Fly.io (free tier)
- **Vector DB**: ChromaDB (runs with backend)
- **PostgreSQL**: Supabase or Neon (if needed, free tier)

### Alternative Options
- **Frontend**: Netlify, Cloudflare Pages
- **Backend**: Railway, Google Cloud Run
- **Vector DB**: Qdrant Cloud (free tier), Pinecone (free tier)

---

## 🚀 Option 1: Vercel + Render (Easiest)

### Step 1: Deploy Frontend to Vercel

1. **Push code to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your repository
   - Select `frontend` as root directory

3. **Configure Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```

4. **Deploy**: Vercel will auto-deploy on every push

### Step 2: Deploy Backend to Render

1. **Create `render.yaml`** in project root:
   ```yaml
   services:
     - type: web
       name: rag-knowledge-base-backend
       env: python
       buildCommand: cd backend && pip install -r requirements.txt
       startCommand: cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
         - key: CHROMA_PATH
           value: /tmp/chroma
         - key: LLM_PROVIDER
           value: groq
         - key: GROQ_API_KEY
           sync: false  # Set in Render dashboard
         - key: EMBEDDING_PROVIDER
           value: local
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New Web Service"
   - Connect your repository
   - Select `render.yaml` or configure manually:
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
     - **Environment**: Python 3

3. **Set Environment Variables** in Render dashboard:
   ```
   GROQ_API_KEY=your_groq_key
   LLM_PROVIDER=groq
   LLM_MODEL=llama-3.1-8b-instant
   EMBEDDING_PROVIDER=local
   CHROMA_PATH=/tmp/chroma
   ```

4. **Update Frontend**: Change `NEXT_PUBLIC_API_URL` in Vercel to your Render URL

**Limitations**:
- Render free tier: Spins down after 15min inactivity
- ChromaDB data is ephemeral (lost on restart)
- First request after spin-down takes ~30s

---

## 🚀 Option 2: Vercel + Fly.io (Better Performance)

### Step 1: Deploy Frontend to Vercel
(Same as Option 1, Step 1)

### Step 2: Deploy Backend to Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `fly.toml`** in `backend/`:
   ```toml
   app = "rag-knowledge-base-backend"
   primary_region = "iad"

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     PORT = "8080"
     CHROMA_PATH = "/data/chroma"
     LLM_PROVIDER = "groq"
     EMBEDDING_PROVIDER = "local"

   [[services]]
     internal_port = 8080
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443

   [[mounts]]
     source = "chroma_data"
     destination = "/data"
   ```

3. **Deploy**:
   ```bash
   cd backend
   fly launch
   # Follow prompts, select region
   fly secrets set GROQ_API_KEY=your_key
   fly deploy
   ```

**Advantages**:
- Faster cold starts than Render
- Persistent volume for ChromaDB
- Better free tier limits

---

## 🚀 Option 3: All-in-One Railway (Simplest)

Railway can deploy both frontend and backend:

1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **New Project → Deploy from GitHub**
4. **Add Services**:
   - **Backend**: Select `backend/` directory
   - **Frontend**: Select `frontend/` directory

5. **Configure Backend**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Set in Railway dashboard

6. **Configure Frontend**:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Environment Variables**: `NEXT_PUBLIC_API_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}`

**Limitations**:
- Railway free tier: $5 credit/month (limited usage)
- ChromaDB data ephemeral unless using volume

---

## 🔧 Configuration Changes Needed

### Backend Changes

1. **Update CORS** in `backend/src/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-frontend.vercel.app",
           "http://localhost:3001",  # Keep for local dev
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Update ChromaDB Path** (for persistent storage):
   - Use `/tmp/chroma` for ephemeral (Render)
   - Use `/data/chroma` with volume (Fly.io, Railway)

3. **Environment Variables**:
   ```bash
   PORT=8080  # Render/Fly.io sets this automatically
   CHROMA_PATH=/tmp/chroma  # or /data/chroma
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key
   EMBEDDING_PROVIDER=local  # Free, no API key needed
   ```

### Frontend Changes

1. **Update API URL** in `frontend/.env.production`:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```

2. **Update `next.config.js`** if needed:
   ```javascript
   module.exports = {
     env: {
       NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
     },
   };
   ```

---

## 📊 Free Tier Comparison

| Service | Free Tier | Limitations |
|---------|-----------|-------------|
| **Vercel** | Unlimited | 100GB bandwidth/month, serverless functions timeout |
| **Render** | Always free | Spins down after 15min, 750hrs/month |
| **Fly.io** | $5 credit/month | 3 shared VMs, 160GB outbound |
| **Railway** | $5 credit/month | Limited compute hours |
| **Netlify** | 100GB bandwidth | 300 build minutes/month |
| **Cloudflare Pages** | Unlimited | Unlimited bandwidth, 500 builds/month |

---

## 🎯 Recommended Setup for Production

### For Best Performance (Still Free):
1. **Frontend**: Vercel (best Next.js support)
2. **Backend**: Fly.io (persistent storage, fast)
3. **Vector DB**: ChromaDB on Fly.io volume
4. **PostgreSQL**: Supabase (if needed, free tier)

### For Simplest Setup:
1. **Frontend**: Vercel
2. **Backend**: Render (easiest, but slower cold starts)

---

## 🔒 Security Considerations

1. **API Keys**: Never commit to Git, use environment variables
2. **CORS**: Configure allowed origins in production
3. **Rate Limiting**: Add rate limiting middleware (see `SECURITY.md`)
4. **HTTPS**: All free tiers provide HTTPS automatically

---

## 📝 Step-by-Step: Vercel + Render (Quick Start)

### 1. Prepare Repository
```bash
# Ensure .env is in .gitignore
git add .
git commit -m "Ready for deployment"
git push
```

### 2. Deploy Backend (Render)
1. Go to render.com → New Web Service
2. Connect GitHub repo
3. Configure:
   - **Name**: `rag-backend`
   - **Environment**: Python 3
   - **Build**: `cd backend && pip install -r requirements.txt`
   - **Start**: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy

### 3. Deploy Frontend (Vercel)
1. Go to vercel.com → New Project
2. Import GitHub repo
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render URL
5. Deploy

### 4. Update CORS
Update `backend/src/main.py` with your Vercel URL and redeploy.

---

## 🐛 Troubleshooting

### Backend not accessible
- Check CORS configuration
- Verify environment variables
- Check Render/Fly.io logs

### ChromaDB data lost
- Use persistent volume (Fly.io) or external service
- Consider Qdrant Cloud or Pinecone for persistent storage

### Cold start slow (Render)
- First request after 15min inactivity takes ~30s
- Use Fly.io for faster cold starts
- Or upgrade to paid tier

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS allows your frontend domain
- Verify backend is running (check health endpoint)

---

## 💡 Tips

1. **Use Groq**: Fast and free LLM, perfect for free tier
2. **Local Embeddings**: No API key needed, works offline
3. **Monitor Usage**: Free tiers have limits, monitor usage
4. **Backup Data**: ChromaDB data is ephemeral on free tiers, backup important data
5. **Optimize**: Use caching, reduce API calls

---

## 📚 Additional Resources

- [Vercel Deployment Docs](https://vercel.com/docs)
- [Render Deployment Docs](https://render.com/docs)
- [Fly.io Deployment Docs](https://fly.io/docs)
- [Railway Deployment Docs](https://docs.railway.app)

---

**Ready to deploy?** Start with Option 1 (Vercel + Render) for the easiest setup!
