# Deployment Guide - Accelyra Closing Platform

This guide covers deploying both the FastAPI backend and Streamlit frontend.

## Architecture Overview

- **Frontend**: Streamlit dashboard (deployed to Streamlit Cloud)
- **Backend**: FastAPI REST API (deployed to Render.com)
- **Database**: SQLite (for demo) - will persist on Render

---

## Option 1: Deploy to Render + Streamlit Cloud (Recommended)

### Step 1: Deploy Backend API to Render

**1. Create Render Account**
- Go to https://render.com
- Sign up with your GitHub account

**2. Create New Web Service**
- Click "New +" → "Web Service"
- Connect your GitHub repository: `snayj/accelyra-closing-platform`
- Configure:
  - **Name**: `accelyra-api`
  - **Environment**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
  - **Plan**: Free

**3. Add Environment Variables** (in Render dashboard)
- `PYTHON_VERSION`: `3.11.0`

**4. Deploy**
- Click "Create Web Service"
- Wait for deployment (3-5 minutes)
- Note your API URL: `https://accelyra-api.onrender.com`

**5. Initialize Database**
After deployment, run seed data via Render Shell:
```bash
python scripts/seed_data.py
```

### Step 2: Deploy Frontend to Streamlit Cloud

**1. Go to Streamlit Cloud**
- Visit https://share.streamlit.io
- Sign in with GitHub

**2. Create New App**
- Click "New app"
- Repository: `snayj/accelyra-closing-platform`
- Branch: `main`
- Main file path: `frontend/dashboard.py`

**3. Configure Environment Variables**
In "Advanced settings" → "Secrets", add:
```toml
API_BASE_URL = "https://accelyra-api.onrender.com/api/v1"
```

**4. Deploy**
- Click "Deploy!"
- Your app will be live at: `https://[your-app-name].streamlit.app`

---

## Option 2: Deploy to Railway (Alternative)

Railway offers simple deployment with automatic HTTPS.

### Backend Deployment

**1. Create Railway Account**
- Go to https://railway.app
- Sign up with GitHub

**2. Create New Project**
- Click "New Project" → "Deploy from GitHub repo"
- Select `accelyra-closing-platform`

**3. Configure**
- Add environment variable:
  - `PORT`: `8000`
- Railway will auto-detect Python and install dependencies

**4. Get Public URL**
- Click "Settings" → "Generate Domain"
- Note the URL: `https://accelyra-api.up.railway.app`

### Frontend Deployment
Same as Option 1 - deploy to Streamlit Cloud with Railway API URL.

---

## Option 3: Run Frontend Locally with Deployed Backend

If you only want to deploy the backend:

**1. Deploy API** (using Render or Railway above)

**2. Update Local Config**
Create `.streamlit/secrets.toml`:
```toml
API_BASE_URL = "https://your-api-url.onrender.com/api/v1"
```

**3. Run Streamlit Locally**
```bash
streamlit run frontend/dashboard.py
```

---

## Testing Deployment

Once both are deployed, test the connection:

1. Visit your Streamlit app URL
2. Check the sidebar - should show "✅ Connected"
3. Try creating a test transaction in the simulator
4. View transaction history

---

## Troubleshooting

### API shows offline in deployed Streamlit app

**Check:**
1. API URL is correct in Streamlit secrets
2. API is deployed and running (visit API URL in browser)
3. CORS is configured correctly (already set in `backend/main.py`)

**Fix:**
- Verify API URL doesn't have trailing slash
- Check Render/Railway logs for errors
- Ensure environment variables are set

### Database not persisting on Render

**Render Free Tier Note:**
- SQLite file persists but service may sleep after inactivity
- First request after sleep will wake service (may take 30 seconds)
- For production, migrate to PostgreSQL

### CORS errors

Already configured in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Render (API) | Free | $0/month |
| Streamlit Cloud | Free | $0/month |
| **Total** | | **$0/month** |

**Limitations:**
- Render free tier: 750 hours/month, sleeps after 15min inactivity
- Streamlit Cloud: Public apps only (code visible on GitHub)

---

## Production Checklist

Before production deployment:

- [ ] Migrate to PostgreSQL (from SQLite)
- [ ] Add authentication/authorization
- [ ] Set up proper environment variables
- [ ] Configure custom domain
- [ ] Add monitoring (e.g., Sentry)
- [ ] Set up CI/CD pipeline
- [ ] Add rate limiting
- [ ] Configure backup strategy
- [ ] Add SSL certificate (auto on Render/Railway)
- [ ] Review security settings

---

## Quick Commands

### Local Development
```bash
# Terminal 1 - API
uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend
streamlit run frontend/dashboard.py --server.port 8501
```

### Seed Data
```bash
python scripts/seed_data.py
```

### Check API Health
```bash
curl https://your-api-url.onrender.com/health
```
