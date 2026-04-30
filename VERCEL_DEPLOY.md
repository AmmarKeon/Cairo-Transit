# Cairo Transit - Vercel Deployment Guide

## Overview
Deploy the Cairo Transit frontend on **Vercel** and the FastAPI backend on **Railway/Render/Fly.io**.

## Architecture
```
Browser → Vercel (Frontend) → Backend on Railway/Render
```

---

## ⚠️ CRITICAL: Complete These Steps in Order

**Step 1 → 2 → 3 — in that order. Skip step 3 and your app won't work.**

### Step 1: Deploy Backend First
### Step 2: Note the Backend URL
### Step 3: Deploy Frontend & Set Environment Variable

---

## Step 1: Deploy the Backend (Choose One)

### Option A: Railway (Recommended)

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. **IMPORTANT**: When creating the project, select **"Blank Project"** first, then go to **Settings → Variables** and add:
   - `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app` (you'll fill this after Step 3)
3. Then go to **Deployments → New Deployment** → Connect GitHub repo
4. Select branch `vercel-deploy` or `Keon0.2`
5. For the **root directory**, leave it as the repo root (or Railway may not find the `data/` directory)
6. Railway auto-detects FastAPI via `backend/requirements.txt`
7. Set the **start command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
8. Note the deployment URL (e.g., `https://cairo-transit.up.railway.app`)

### Option B: Render

1. Go to [render.com](https://render.com) → Sign up
2. Create **Web Service** → Connect GitHub repo
3. Root directory: leave empty (repo root)
4. Build command: `cd backend && pip install -r requirements.txt`
5. Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variable: `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app`
7. Note the backend URL when deployment completes

### Option C: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. In the project root (not backend/): `fly launch`
3. `fly deploy`
4. Add: `fly secrets set ALLOWED_ORIGINS=https://your-frontend.vercel.app`

---

## Step 2: Note Your Backend URL

After the backend deploys, copy its URL. Examples:
- Railway: `https://cairo-transit.railway.app`
- Render: `https://cairo-transit.onrender.com`

You'll need this for Step 3.

---

## Step 3: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Click **"Add New..." → Project** → Import `AmmarKeon/Cairo-Transit`
3. Select branch: `vercel-deploy`
4. Vercel should auto-detect **Vite** as the framework
5. Configure:
   - **Root Directory**: `.` (repo root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
6. Click **Deploy**

### Set the Environment Variable (CRITICAL!)

After deployment (or before, same result):

1. In Vercel dashboard → Your project → **Settings** → **Environment Variables**
2. Add:
   - **Name**: `VITE_API_URL`
   - **Value**: Your backend URL from Step 2 (e.g., `https://cairo-transit.railway.app`)
   - **Environments**: Select **Production**, **Preview**, and **Development**
3. Click **Save**
4. Go to **Deployments** → Click **"..."** on the latest → **Redeploy**
5. Wait for redeploy to complete

---

## Step 4: Update Backend CORS

After getting your Vercel frontend URL:

1. Go to your backend hosting (Railway/Render)
2. Update the `ALLOWED_ORIGINS` environment variable:
   - If using Vercel default domain: `https://your-project.vercel.app`
   - If using a custom domain: `https://your-domain.com`
3. Redeploy the backend

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

For local frontend testing against the production backend:
```bash
cd frontend
VITE_API_URL=https://your-backend.railway.app npm run dev
```

---

## Troubleshooting

### Blank page after deployment
- Check Vercel build log for errors
- Verify build command and output directory are correct

### "Cannot connect to server" in browser console
- **Cause**: `VITE_API_URL` not set or set incorrectly
- **Fix**: Set it in Vercel dashboard → Settings → Environment Variables, then redeploy

### API calls return CORS error
- **Cause**: `ALLOWED_ORIGINS` on backend doesn't include your Vercel domain
- **Fix**: Update `ALLOWED_ORIGINS` on your backend hosting platform

### Backend returns empty data / 500 errors
- **Cause**: `data/` directory missing on backend deployment
- **Fix**: Make sure the backend deployment includes the repo root (not just `backend/` subdirectory)

### Backend URL returns "Not Found"
- **Cause**: Wrong URL path — the backend serves at `/` not `/api/`
- **Fix**: The API endpoints are at `https://backend-url/api/nodes`, etc.
