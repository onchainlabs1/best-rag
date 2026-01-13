# 🚀 Quick Deploy Guide (Free)

Deploy your RAG Knowledge Base online for free in 5 minutes!

## ⚡ Fastest Option: Vercel + Render

### Step 1: Deploy Backend (Render) - 2 min

1. **Go to [render.com](https://render.com)** → Sign up with GitHub
2. **New Web Service** → Connect your GitHub repo
3. **Configure**:
   - **Name**: `rag-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** (add these):
   ```
   GROQ_API_KEY=your_groq_key_here
   LLM_PROVIDER=groq
   LLM_MODEL=llama-3.1-8b-instant
   EMBEDDING_PROVIDER=local
   CHROMA_PATH=/tmp/chroma
   CORS_ORIGINS=*
   ```
5. **Deploy** → Copy your backend URL (e.g., `https://rag-backend.onrender.com`)

### Step 2: Deploy Frontend (Vercel) - 2 min

1. **Go to [vercel.com](https://vercel.com)** → Sign up with GitHub
2. **New Project** → Import your GitHub repo
3. **Configure**:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://rag-backend.onrender.com
   ```
5. **Deploy** → Copy your frontend URL

### Step 3: Update CORS - 1 min

1. **Go back to Render dashboard**
2. **Update Environment Variable**:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3001
   ```
3. **Redeploy** backend

### ✅ Done!

Your app is now live at: `https://your-frontend.vercel.app`

---

## 🎯 Alternative: All-in-One Railway

1. **Go to [railway.app](https://railway.app)** → Sign up
2. **New Project** → Deploy from GitHub
3. **Add Backend Service**:
   - Root: `backend/`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. **Add Frontend Service**:
   - Root: `frontend/`
   - Build: `npm install && npm run build`
   - Start: `npm start`
5. **Set Environment Variables** (same as above)

---

## 📝 Notes

- **Render free tier**: Spins down after 15min inactivity (first request takes ~30s)
- **Vercel**: Unlimited, always fast
- **ChromaDB data**: Ephemeral on free tiers (lost on restart)
- **Groq API**: Free, fast, perfect for free tier

---

## 🔧 Troubleshooting

**Backend not accessible?**
- Check Render logs
- Verify environment variables
- Check CORS configuration

**Frontend can't connect?**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS allows your Vercel domain

**Cold start slow?**
- Normal on Render free tier (first request after 15min)
- Use Fly.io for faster cold starts (see `DEPLOYMENT.md`)

---

**Need more details?** See `DEPLOYMENT.md` for complete guide!
