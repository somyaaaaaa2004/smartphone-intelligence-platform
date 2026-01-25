# 🚀 Quick Deployment - Get Your Live Link in 5 Minutes!

## Step-by-Step: Deploy to Railway (Easiest Method)

### Step 1: Push to GitHub (2 minutes)

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (3 minutes)

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select your repository**
5. Railway will automatically:
   - Detect the Dockerfile
   - Start building your app
   - Provide a live URL

### Step 3: Add Environment Variables

In Railway dashboard:
1. Click on your service
2. Go to **"Variables"** tab
3. Add these variables:

```
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=PUBLIC
ENVIRONMENT=production
```

4. Railway will automatically redeploy

### Step 4: Get Your Live Link! 🎉

Railway provides a URL like:
```
https://your-app-name.up.railway.app
```

**That's your live link!** ✅

### Step 5: Test Your Live API

```bash
# Health check
curl https://your-app-name.up.railway.app/health

# API docs
https://your-app-name.up.railway.app/docs

# Test endpoints
curl https://your-app-name.up.railway.app/macro/IND
curl https://your-app-name.up.railway.app/companies
```

## 🎯 Alternative: Render (Free Tier)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your repo
5. Render auto-detects `render.yaml`
6. Add environment variables
7. Deploy!

**Your link**: `https://your-app-name.onrender.com`

## ✅ Pre-Deployment Checklist

- [x] ✅ Code is working (all fixes applied)
- [x] ✅ Dockerfile created
- [x] ✅ Gunicorn config ready
- [x] ✅ Environment variables documented
- [x] ✅ Health check endpoint working
- [x] ✅ No linter errors

## 🔧 Troubleshooting

**Build fails?**
- Check Railway logs
- Verify Python 3.13 in Dockerfile
- Ensure all dependencies in requirements.txt

**App crashes?**
- Check environment variables are set
- Verify Snowflake credentials
- Check logs in Railway dashboard

**Health check fails?**
- Ensure `/health` endpoint works
- Check Snowflake connection
- Verify all env vars are set

## 📱 Update Dashboard to Use Live API

After deployment, update your Streamlit dashboard:

```python
# In dashboard/app.py, change:
API_BASE_URL = os.getenv("API_URL", "https://your-app-name.up.railway.app")
```

Or set environment variable:
```bash
export API_URL=https://your-app-name.up.railway.app
```

## 🎉 You're Done!

Your project is now live! Share your link:
```
https://your-app-name.up.railway.app
```

---

**Need help?** Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.
