# 🚀 Quick Deploy to Render (Free Alternative to Railway)

## Step-by-Step: Get Your Live Link in 5 Minutes

### Step 1: Push to GitHub (2 minutes)

```bash
# If not already on GitHub
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy on Render (3 minutes)

1. **Go to Render**: https://render.com
2. **Sign up/Login** with your **GitHub account** (one-click)
3. **Click "New"** → **"Web Service"**
4. **Connect your GitHub repository**
   - Select your repository
   - Render will auto-detect `render.yaml` ✅
5. **Configure** (if needed):
   - **Name**: `smartphone-intelligence-api` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.main:app -c gunicorn.conf.py --bind 0.0.0.0:$PORT`

### Step 3: Add Environment Variables

In Render dashboard:
1. Go to your service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add these one by one:

```
SNOWFLAKE_ACCOUNT = your_snowflake_account
SNOWFLAKE_USER = your_snowflake_user
SNOWFLAKE_PASSWORD = your_snowflake_password
SNOWFLAKE_WAREHOUSE = your_warehouse_name
SNOWFLAKE_DATABASE = your_database_name
SNOWFLAKE_SCHEMA = PUBLIC
ENVIRONMENT = production
```

5. Click **"Save Changes"** - Render will auto-redeploy

### Step 4: Get Your Live Link! 🎉

Render provides a URL like:
```
https://smartphone-intelligence-api.onrender.com
```

**That's your live link!** ✅

### Step 5: Test Your Live API

```bash
# Health check
curl https://smartphone-intelligence-api.onrender.com/health

# API docs
https://smartphone-intelligence-api.onrender.com/docs

# Test endpoints
curl https://smartphone-intelligence-api.onrender.com/macro/IND
curl https://smartphone-intelligence-api.onrender.com/companies
```

## ⚠️ Important Notes

1. **Free Tier Behavior**:
   - App spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds
   - This is normal for free tier

2. **Upgrade Options**:
   - Paid plans ($7/month) keep app always-on
   - Free tier is perfect for testing/demos

3. **Custom Domain**:
   - Free tier supports custom domains
   - Go to Settings → Custom Domain

## 🎯 Alternative: Fly.io (Always-On Free Tier)

If you need always-on without spin-down:

1. **Install Fly CLI**
   ```powershell
   # Windows PowerShell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Deploy**
   ```bash
   fly launch
   # Follow prompts, then:
   fly secrets set SNOWFLAKE_ACCOUNT=your_account
   fly secrets set SNOWFLAKE_USER=your_user
   fly secrets set SNOWFLAKE_PASSWORD=your_password
   fly secrets set SNOWFLAKE_WAREHOUSE=your_warehouse
   fly secrets set SNOWFLAKE_DATABASE=your_database
   fly secrets set SNOWFLAKE_SCHEMA=PUBLIC
   fly deploy
   ```

4. **Get Link**
   ```bash
   fly open
   # Or: https://smartphone-intelligence-api.fly.dev
   ```

## 📱 Deploy Dashboard on Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign up** with GitHub
3. **New app** → Select your repo
4. **Main file**: `dashboard/app.py`
5. **Add secrets**:
   ```toml
   API_URL = "https://smartphone-intelligence-api.onrender.com"
   ```
6. **Deploy!**

**Dashboard link**: `https://your-dashboard.streamlit.app`

## 🎉 You're Done!

Your project is now live on Render! Share your link:
```
https://smartphone-intelligence-api.onrender.com
```

---

**Need help?** Check [DEPLOYMENT_ALTERNATIVES.md](DEPLOYMENT_ALTERNATIVES.md) for more options.
