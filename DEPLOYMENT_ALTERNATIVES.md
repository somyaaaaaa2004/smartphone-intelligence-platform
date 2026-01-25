# 🚀 Free Deployment Alternatives (Railway Not Working)

Since Railway free tier is not working, here are **better free alternatives** with step-by-step guides:

## 🎯 Option 1: Render (BEST FREE ALTERNATIVE) ⭐

**Why Render?**
- ✅ **Free tier available** (spins down after 15 min inactivity, but free)
- ✅ **Automatic SSL/HTTPS**
- ✅ **Easy GitHub integration**
- ✅ **No credit card required**
- ✅ **Auto-detects your `render.yaml`**

### Quick Deploy Steps:

1. **Push to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to https://render.com
   - Sign up/Login with **GitHub**
   - Click **"New"** → **"Web Service"**
   - Connect your GitHub repository
   - Render will **auto-detect** `render.yaml` ✅

3. **Configure Settings**
   - **Name**: `smartphone-intelligence-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.main:app -c gunicorn.conf.py --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**
   In Render dashboard → Environment tab, add:
   ```
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=PUBLIC
   SNOWFLAKE_ROLE=your_role (optional)
   PORT=8000
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   ```

5. **Deploy!**
   - Click **"Create Web Service"**
   - Render will build and deploy automatically
   - **Your live link**: `https://smartphone-intelligence-api.onrender.com`

**Note**: Free tier spins down after 15 min inactivity. First request may take 30-60 seconds to wake up.

---

## 🎯 Option 2: Fly.io (Great Free Tier) ⭐

**Why Fly.io?**
- ✅ **Generous free tier** (3 shared VMs, 3GB storage)
- ✅ **Always-on option** (with some limits)
- ✅ **Global deployment**
- ✅ **No credit card required for free tier**

### Quick Deploy Steps:

1. **Install Fly CLI**
   ```powershell
   # Windows: Download from https://fly.io/docs/getting-started/installing-flyctl/
   # Or use PowerShell:
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Deploy**
   ```bash
   # Initialize (first time only)
   fly launch
   
   # Follow prompts:
   # - App name: smartphone-intelligence-api
   # - Region: Choose closest (e.g., iad for US East)
   # - Don't deploy yet (we'll set secrets first)
   ```

4. **Set Environment Variables (Secrets)**
   ```bash
   fly secrets set SNOWFLAKE_ACCOUNT=your_account
   fly secrets set SNOWFLAKE_USER=your_user
   fly secrets set SNOWFLAKE_PASSWORD=your_password
   fly secrets set SNOWFLAKE_WAREHOUSE=your_warehouse
   fly secrets set SNOWFLAKE_DATABASE=your_database
   fly secrets set SNOWFLAKE_SCHEMA=PUBLIC
   fly secrets set ENVIRONMENT=production
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

6. **Get Your Live Link**
   ```bash
   fly open
   # Or check: https://smartphone-intelligence-api.fly.dev
   ```

---

## 🎯 Option 3: Streamlit Cloud (For Dashboard Only)

**Why Streamlit Cloud?**
- ✅ **100% free forever**
- ✅ **Automatic deployments from GitHub**
- ✅ **Perfect for Streamlit apps**
- ✅ **No configuration needed**

### Deploy Dashboard Only:

1. **Push to GitHub** (if not already done)

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign up/Login with **GitHub**
   - Click **"New app"**
   - Select your repository
   - **Main file path**: `dashboard/app.py`
   - **Python version**: 3.13 (or latest available)

3. **Add Environment Variables**
   In Streamlit Cloud → Settings → Secrets, add:
   ```toml
   [secrets]
   API_URL = "https://your-api-url.onrender.com"
   SNOWFLAKE_ACCOUNT = "your_account"
   SNOWFLAKE_USER = "your_user"
   SNOWFLAKE_PASSWORD = "your_password"
   SNOWFLAKE_WAREHOUSE = "your_warehouse"
   SNOWFLAKE_DATABASE = "your_database"
   SNOWFLAKE_SCHEMA = "PUBLIC"
   ```

4. **Deploy!**
   - Click **"Deploy"**
   - **Your dashboard link**: `https://your-app-name.streamlit.app`

**Note**: Deploy API on Render/Fly.io first, then use that URL in Streamlit Cloud secrets.

---

## 🎯 Option 4: PythonAnywhere (Free Tier)

**Why PythonAnywhere?**
- ✅ **Free tier available**
- ✅ **Always-on web apps**
- ✅ **Good for Python apps**

### Quick Deploy Steps:

1. **Sign up**: https://www.pythonanywhere.com
2. **Upload your code** via Git or file upload
3. **Create Web App**:
   - Go to Web tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Python 3.13 (or latest available)
4. **Create WSGI file** (see `pythonanywhere_config.py`)
5. **Set environment variables** in Web app settings
6. **Reload web app**

**Your link**: `https://yourusername.pythonanywhere.com`

---

## 🎯 Option 5: Google Cloud Run (Free Tier)

**Why Cloud Run?**
- ✅ **Generous free tier** (2 million requests/month)
- ✅ **Always-on option**
- ✅ **Automatic scaling**

### Quick Deploy Steps:

1. **Install Google Cloud SDK**
   ```bash
   # Download from https://cloud.google.com/sdk/docs/install
   ```

2. **Login and Setup**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Deploy**
   ```bash
   gcloud run deploy smartphone-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars SNOWFLAKE_ACCOUNT=your_account,SNOWFLAKE_USER=your_user,...
   ```

**Your link**: `https://smartphone-api-xxxxx-uc.a.run.app`

---

## 📊 Comparison Table

| Platform | Free Tier | Always-On | Ease of Use | Best For |
|----------|-----------|-----------|-------------|----------|
| **Render** | ✅ Yes | ⚠️ Spins down | ⭐⭐⭐⭐⭐ | **Recommended** |
| **Fly.io** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ | Production |
| **Streamlit Cloud** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐⭐ | Dashboard only |
| **PythonAnywhere** | ✅ Yes | ✅ Yes | ⭐⭐⭐ | Simple apps |
| **Cloud Run** | ✅ Yes | ✅ Yes | ⭐⭐⭐ | Enterprise |

## 🎯 My Recommendation

**For API**: Use **Render** (easiest) or **Fly.io** (more reliable)
**For Dashboard**: Use **Streamlit Cloud** (perfect for Streamlit)

### Recommended Setup:
1. **Deploy API on Render** → `https://smartphone-api.onrender.com`
2. **Deploy Dashboard on Streamlit Cloud** → `https://your-dashboard.streamlit.app`
3. **Set API_URL in Streamlit Cloud** to point to Render API

---

## 🚀 Quick Start: Render (Recommended)

1. **Go to**: https://render.com
2. **Sign up** with GitHub
3. **New** → **Web Service**
4. **Connect repo**
5. **Add environment variables**
6. **Deploy!**

**Your live link**: `https://smartphone-intelligence-api.onrender.com`

---

## 📝 Environment Variables Checklist

Make sure to set these in your chosen platform:

**Required:**
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA=PUBLIC`

**Optional:**
- `SNOWFLAKE_ROLE`
- `PORT` (usually auto-set)
- `ENVIRONMENT=production`

---

## 🆘 Troubleshooting

**Render:**
- First request slow? Normal - free tier spins down after inactivity
- Build fails? Check Python version (3.13) and requirements.txt

**Fly.io:**
- Deploy fails? Check `fly.toml` configuration
- App crashes? Check secrets are set: `fly secrets list`

**Streamlit Cloud:**
- Dashboard errors? Check API_URL is correct
- Import errors? Verify all packages in requirements.txt

---

**Ready?** Start with **Render** - it's the easiest! 🚀
