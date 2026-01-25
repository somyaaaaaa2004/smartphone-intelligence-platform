# Deployment Guide - Smartphone Intelligence Platform

This guide provides step-by-step instructions to deploy your project to various cloud platforms and get a live link.

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended - Easiest) ⭐

**Railway** is the easiest platform with automatic deployments from GitHub.

#### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment Variables**
   In Railway dashboard, go to your service → Variables tab and add:
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

4. **Get Your Live Link**
   - Railway automatically provides a URL like: `https://your-app-name.up.railway.app`
   - You can also set a custom domain in Settings

**Cost**: Free tier available, then pay-as-you-go

---

### Option 2: Render

**Render** offers free tier with automatic SSL.

#### Steps:

1. **Push to GitHub** (same as Railway)

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Configure Environment Variables**
   Add the same environment variables as Railway in the Render dashboard

4. **Get Your Live Link**
   - Render provides: `https://your-app-name.onrender.com`
   - Free tier includes SSL automatically

**Cost**: Free tier available (spins down after 15 min inactivity), paid plans available

---

### Option 3: Heroku

**Heroku** is a popular platform with good documentation.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SNOWFLAKE_ACCOUNT=your_account
   heroku config:set SNOWFLAKE_USER=your_user
   heroku config:set SNOWFLAKE_PASSWORD=your_password
   heroku config:set SNOWFLAKE_WAREHOUSE=your_warehouse
   heroku config:set SNOWFLAKE_DATABASE=your_database
   heroku config:set SNOWFLAKE_SCHEMA=PUBLIC
   heroku config:set ENVIRONMENT=production
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Get Your Live Link**
   - Heroku provides: `https://your-app-name.herokuapp.com`

**Cost**: Free tier discontinued, paid plans start at $5/month

---

### Option 4: Fly.io

**Fly.io** offers global deployment with free tier.

#### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows: Download from https://fly.io/docs/getting-started/installing-flyctl/
   ```

2. **Create App**
   ```bash
   fly launch
   ```

3. **Set Secrets**
   ```bash
   fly secrets set SNOWFLAKE_ACCOUNT=your_account
   fly secrets set SNOWFLAKE_USER=your_user
   fly secrets set SNOWFLAKE_PASSWORD=your_password
   fly secrets set SNOWFLAKE_WAREHOUSE=your_warehouse
   fly secrets set SNOWFLAKE_DATABASE=your_database
   fly secrets set SNOWFLAKE_SCHEMA=PUBLIC
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

**Cost**: Free tier available

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [x] ✅ All code fixes applied (`.str` accessor issues fixed)
- [x] ✅ No linter errors
- [x] ✅ Environment variables documented in `.env.example`
- [x] ✅ Dockerfile created
- [x] ✅ Gunicorn configuration ready
- [x] ✅ Health check endpoint working (`/health`)

## 🔧 Environment Variables Required

Make sure to set these in your cloud platform:

**Required:**
- `SNOWFLAKE_ACCOUNT` - Your Snowflake account identifier
- `SNOWFLAKE_USER` - Snowflake username
- `SNOWFLAKE_PASSWORD` - Snowflake password
- `SNOWFLAKE_WAREHOUSE` - Snowflake warehouse name
- `SNOWFLAKE_DATABASE` - Snowflake database name
- `SNOWFLAKE_SCHEMA` - Snowflake schema (usually `PUBLIC`)

**Optional:**
- `SNOWFLAKE_ROLE` - Snowflake role (if needed)
- `PORT` - Server port (usually auto-set by platform)
- `ENVIRONMENT` - Set to `production`
- `API_HOST` - Set to `0.0.0.0`

## 🧪 Testing Your Deployment

After deployment, test your live link:

1. **Health Check**
   ```
   https://your-app-url.com/health
   ```
   Should return: `{"status": "healthy", "api": "running", ...}`

2. **API Endpoints**
   ```
   https://your-app-url.com/
   https://your-app-url.com/docs
   https://your-app-url.com/macro/IND
   https://your-app-url.com/companies
   ```

3. **Update Dashboard**
   Update `API_URL` in your Streamlit dashboard to point to your live API:
   ```python
   API_URL = "https://your-app-url.com"
   ```

## 🎯 Recommended: Railway Deployment

**Why Railway?**
- ✅ Easiest setup (just connect GitHub)
- ✅ Automatic deployments
- ✅ Free tier available
- ✅ Automatic HTTPS/SSL
- ✅ Good documentation
- ✅ No credit card required for free tier

**Quick Start:**
1. Push code to GitHub
2. Go to railway.app
3. Connect GitHub repo
4. Add environment variables
5. Deploy! 🚀

Your live link will be: `https://your-app-name.up.railway.app`

## 📝 Post-Deployment

After deployment:

1. **Test all endpoints** using the live URL
2. **Update dashboard** `API_URL` to point to live API
3. **Monitor logs** in your platform's dashboard
4. **Set up alerts** for health check failures
5. **Configure custom domain** (optional)

## 🆘 Troubleshooting

### Common Issues:

1. **Build fails**
   - Check Python version (should be 3.13)
   - Verify all dependencies in `requirements.txt`

2. **App crashes on startup**
   - Check environment variables are set
   - Verify Snowflake credentials
   - Check logs in platform dashboard

3. **Health check fails**
   - Ensure `/health` endpoint is accessible
   - Check Snowflake connection
   - Verify all required env vars are set

4. **Port binding errors**
   - Platform sets `PORT` automatically
   - Ensure `gunicorn.conf.py` uses `os.getenv('PORT')`

## 📞 Support

If you encounter issues:
1. Check platform logs
2. Verify environment variables
3. Test locally first: `python -m uvicorn backend.main:app --port 8000`
4. Check `/health` endpoint

---

**Ready to deploy?** Choose Railway for the easiest experience! 🚀
