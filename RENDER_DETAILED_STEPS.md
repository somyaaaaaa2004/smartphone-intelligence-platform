# Render Deployment - Complete Step-by-Step Guide

This guide walks you through deploying your Smartphone Intelligence Platform on Render, step by step.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] GitHub account
- [ ] Render account (sign up at https://render.com - free tier works)
- [ ] Your code pushed to GitHub (already done: `somyaaaaaa2004/smartphone-intelligence-platform`)
- [ ] Snowflake credentials ready:
  - Account identifier (e.g., `MOPRGFY-EE19523`)
  - Username
  - Password
  - Warehouse name
  - Database name
  - Schema name (usually `PUBLIC`)

---

## 🎯 Overview

You'll create **TWO separate services** on Render:

1. **Backend API** (FastAPI) - Connects to Snowflake, serves data
2. **Dashboard** (Streamlit) - Connects to Backend API, displays charts

**Important:** Deploy backend FIRST, then dashboard (dashboard needs backend URL).

---

## 📘 PART 1: Deploy Backend API Service

### Step 1.1: Access Render Dashboard

1. Open your web browser
2. Go to: **https://dashboard.render.com**
3. Log in with your Render account
   - If you don't have an account, click **"Sign Up"** (free tier is fine)

### Step 1.2: Create New Web Service

1. In the Render dashboard, look at the top right corner
2. Click the **"New +"** button (blue button with plus icon)
3. A dropdown menu will appear
4. Click **"Web Service"** from the dropdown

**What you'll see:** A page titled "Create a New Web Service"

### Step 1.3: Connect GitHub Repository

1. On the "Create a New Web Service" page, you'll see options to connect a repository
2. You'll see a section asking to connect a Git repository
3. Click **"Connect account"** or **"Connect GitHub"** button
   - If you haven't connected GitHub before, Render will ask for GitHub permissions
   - Click **"Authorize Render"** to grant access
4. After connecting, you'll see a list of your GitHub repositories
5. Find and click on: **`somyaaaaaa2004/smartphone-intelligence-platform`**
6. Click **"Connect"** button next to the repository

**What you'll see:** The repository is now connected, and Render shows repository details

### Step 1.4: Configure Basic Settings

Fill in the following fields:

**Name:**
- Type: `smartphone-intelligence-api`
- This will be part of your service URL

**Region:**
- Select: **Oregon (US West)** or closest to you
- This affects latency

**Branch:**
- Select: **`main`** (or `master` if that's your default branch)

**Root Directory:**
- Leave this **EMPTY** (default)

**Runtime:**
- Select: **Docker**

**Dockerfile Path:**
- Type: `./Dockerfile.api`
- This tells Render which Dockerfile to use

**Docker Context:**
- Leave this **EMPTY** or type: `.`
- This is the build context

**Instance Type:**
- Select: **Free** (or upgrade to paid if needed)

### Step 1.5: Configure Advanced Settings

Scroll down to find **"Advanced"** section and expand it:

**Health Check Path:**
- Type: `/health`
- This endpoint will be checked to verify service is running

**Auto-Deploy:**
- Select: **Yes**
- This automatically deploys when you push to GitHub

**Pull Request Previews:**
- Leave as default (optional)

### Step 1.6: Set Environment Variables

**CRITICAL STEP:** This is where you configure Snowflake connection.

1. Scroll to the **"Environment Variables"** section
2. Click **"Add Environment Variable"** button
3. Add each variable one by one:

**Variable 1:**
- Key: `PORT`
- Value: `8000`
- Click **"Add"**

**Variable 2:**
- Key: `ENVIRONMENT`
- Value: `production`
- Click **"Add"**

**Variable 3:**
- Key: `LOG_LEVEL`
- Value: `INFO`
- Click **"Add"**

**Variable 4:**
- Key: `SNOWFLAKE_ACCOUNT`
- Value: `MOPRGFY-EE19523` (replace with YOUR Snowflake account)
- Click **"Add"**

**Variable 5:**
- Key: `SNOWFLAKE_USER`
- Value: `your_snowflake_username` (replace with YOUR username)
- Click **"Add"**

**Variable 6:**
- Key: `SNOWFLAKE_PASSWORD`
- Value: `your_snowflake_password` (replace with YOUR password)
- Click **"Add"**
- ⚠️ **Important:** This is sensitive - Render will mask it in the UI

**Variable 7:**
- Key: ``
- Value: `your_warehouse_name` (replace with YOUR warehouse)
- Click **"Add"**

**Variable 8:**
- Key: `SNOWFLAKE_DATABASE`
- Value: `SMARTPHONE_INTELLIGENCE_DB` (or your database name)
- Click **"Add"**

**Variable 9:**
- Key: `SNOWFLAKE_SCHEMA`
- Value: `PUBLIC`
- Click **"Add"**

**Variable 10 (Optional):**
- Key: `SNOWFLAKE_ROLE`
- Value: `SMARTPHONE_ROLE` (or your role name, if using custom role)
- Click **"Add"**

**After adding all variables, you should see a list like:**
```
PORT = 8000
ENVIRONMENT = production
LOG_LEVEL = INFO
SNOWFLAKE_ACCOUNT = MOPRGFY-EE19523
SNOWFLAKE_USER = your_user
SNOWFLAKE_PASSWORD = ******** (masked)
SNOWFLAKE_WAREHOUSE = your_warehouse
SNOWFLAKE_DATABASE = SMARTPHONE_INTELLIGENCE_DB
SNOWFLAKE_SCHEMA = PUBLIC
SNOWFLAKE_ROLE = SMARTPHONE_ROLE
```

### Step 1.7: Create and Deploy Backend Service

1. Scroll to the bottom of the page
2. Review all your settings one more time
3. Click the **"Create Web Service"** button (blue button at bottom)

**What happens next:**
- Render will start building your service
- You'll see a build log showing progress
- Build typically takes 5-10 minutes
- You'll see messages like:
  - "Building Docker image..."
  - "Installing dependencies..."
  - "Starting service..."

### Step 1.8: Wait for Deployment

1. **DO NOT CLOSE** the browser tab
2. Watch the build logs
3. Look for these success indicators:
   - ✅ "Build successful"
   - ✅ "Service is live"
   - ✅ Status changes to **"Live"** (green)

**If build fails:**
- Check the error logs
- Common issues:
  - Wrong Dockerfile path → Check `./Dockerfile.api` exists
  - Missing environment variables → Verify all Snowflake vars are set
  - Build timeout → Free tier has limits, wait and retry

### Step 1.9: Copy Backend Service URL

**CRITICAL:** You need this URL for the dashboard!

1. Once deployment shows **"Live"** status
2. Look at the top of the service page
3. You'll see a URL like: `https://smartphone-intelligence-api.onrender.com`
4. **COPY THIS URL** - you'll need it in Part 2
5. Save it somewhere safe (notepad, notes app, etc.)

**Example URL format:**
```
https://smartphone-intelligence-api.onrender.com
```

### Step 1.10: Test Backend Service

Before proceeding, verify backend works:

1. **Test Root Endpoint:**
   - Open: `https://smartphone-intelligence-api.onrender.com/`
   - Should show: `{"service": "Smartphone Intelligence Platform API", "status": "running", "docs": "/docs"}`

2. **Test Health Endpoint:**
   - Open: `https://smartphone-intelligence-api.onrender.com/health`
   - Should show: `{"status": "healthy", "api": "running", ...}`

3. **Test API Docs:**
   - Open: `https://smartphone-intelligence-api.onrender.com/docs`
   - Should show Swagger UI with API documentation

**If any test fails:**
- Check service logs in Render dashboard
- Verify Snowflake credentials are correct
- Check health endpoint for specific errors

---

## 📗 PART 2: Deploy Dashboard Service

### Step 2.1: Create Second Web Service

1. In Render dashboard, click **"New +"** button again (top right)
2. Click **"Web Service"** from dropdown
3. You'll see the "Create a New Web Service" page again

### Step 2.2: Connect Same GitHub Repository

1. In the repository selection, find: **`somyaaaaaa2004/smartphone-intelligence-platform`**
2. Click **"Connect"** (same repository as before)

### Step 2.3: Configure Dashboard Basic Settings

Fill in these fields:

**Name:**
- Type: `smartphone-intelligence-dashboard`
- This will be your dashboard URL

**Region:**
- Select: **Same region as backend** (Oregon if you used that)
- This reduces latency between services

**Branch:**
- Select: **`main`** (same as backend)

**Root Directory:**
- Leave **EMPTY**

**Runtime:**
- Select: **Docker**

**Dockerfile Path:**
- Type: `./Dockerfile`
- ⚠️ **Different from backend!** This uses the Streamlit Dockerfile

**Docker Context:**
- Leave **EMPTY** or type: `.`

**Instance Type:**
- Select: **Free**

### Step 2.4: Configure Dashboard Advanced Settings

Expand **"Advanced"** section:

**Health Check Path:**
- Type: `/_stcore/health`
- This is Streamlit's health check endpoint

**Auto-Deploy:**
- Select: **Yes**

### Step 2.5: Set Dashboard Environment Variables

**CRITICAL:** Set `BACKEND_API_URL` to your backend URL from Step 1.9!

1. Scroll to **"Environment Variables"** section
2. Click **"Add Environment Variable"**

**Variable 1:**
- Key: `PORT`
- Value: `8501`
- Click **"Add"**

**Variable 2:**
- Key: `ENVIRONMENT`
- Value: `production`
- Click **"Add"**

**Variable 3:**
- Key: `LOG_LEVEL`
- Value: `INFO`
- Click **"Add"`

**Variable 4 (MOST IMPORTANT):**
- Key: `BACKEND_API_URL`
- Value: `https://smartphone-intelligence-api.onrender.com`
  - ⚠️ **Replace with YOUR actual backend URL from Step 1.9!**
  - Example: If your backend is `https://smartphone-intelligence-api-abc123.onrender.com`, use that
- Click **"Add"**

**After adding, you should see:**
```
PORT = 8501
ENVIRONMENT = production
LOG_LEVEL = INFO
BACKEND_API_URL = https://smartphone-intelligence-api.onrender.com
```

### Step 2.6: Create and Deploy Dashboard Service

1. Scroll to bottom
2. Review settings
3. Click **"Create Web Service"** button

**What happens:**
- Render builds the dashboard service
- Build takes 5-10 minutes
- Watch the build logs

### Step 2.7: Wait for Dashboard Deployment

1. Monitor build logs
2. Wait for **"Live"** status (green)
3. Look for success messages

### Step 2.8: Copy Dashboard Service URL

1. Once **"Live"**, find the dashboard URL at top of page
2. URL format: `https://smartphone-intelligence-dashboard.onrender.com`
3. **COPY THIS URL** - this is your live dashboard!

---

## ✅ PART 3: Verify Deployment

### Step 3.1: Test Dashboard URL

1. Open dashboard URL in browser: `https://smartphone-intelligence-dashboard.onrender.com`
2. Wait for page to load (may take 30 seconds on first load - free tier spins down)

### Step 3.2: Check API Status Indicator

Look at the **top of the dashboard page**:

**✅ Success indicators:**
- Green badge showing: **"✅ API Available"**
- API URL in caption shows your Render backend URL (NOT localhost)
- No red error messages

**❌ If you see errors:**
- **"❌ API Unavailable"** → Check `BACKEND_API_URL` is set correctly
- **"API Not Configured"** → `BACKEND_API_URL` environment variable missing
- **Connection errors** → Verify backend service is running

### Step 3.3: Verify KPI Cards

Scroll down and check the **Key Performance Indicators** section:

**✅ Success indicators:**
- All 4 KPI cards show values (not "N/A")
- Values are formatted (e.g., "$3.9T", "$383B")
- May show "📊 Cached data" caption (this is OK - means fallback is working)

**❌ If you see "N/A":**
- API connection issue
- Check backend logs
- Verify `BACKEND_API_URL` is correct

### Step 3.4: Verify Charts Load

Scroll to **"Comparative Analysis"** section:

**✅ Success indicators:**
- GDP chart shows India vs Brazil comparison
- Revenue chart shows Apple vs Samsung comparison
- Charts are interactive (hover works)
- Download buttons are present

**❌ If charts don't load:**
- Check browser console (F12) for errors
- Verify backend is responding
- Charts should still show with fallback data (cached badges)

### Step 3.5: Verify Forecast Section

Scroll to **"Revenue Forecasts"** section:

**✅ Success indicators:**
- Forecast chart displays
- Shows historical data (solid line)
- Shows forecast data (dashed line)
- May show "📈 Estimated Forecast" badge (this is OK - means using linear regression fallback)

### Step 3.6: Check Sidebar

Look at the **left sidebar**:

**✅ Success indicators:**
- Settings section visible
- API Configuration shows your Render backend URL
- No localhost references
- API status shows "Available" (if API is connected)

### Step 3.7: Verify No Localhost References

**Critical check:** Ensure no localhost URLs are visible:

1. Check API status indicator - should show Render URL
2. Check sidebar API configuration - should show Render URL
3. Check browser address bar - should show Render dashboard URL
4. Open browser console (F12) - no localhost errors

**✅ Success:** All URLs are Render URLs, no localhost

---

## 🔧 Troubleshooting Common Issues

### Issue 1: Backend Build Fails

**Symptoms:**
- Build log shows errors
- Service status stays "Building" or shows "Failed"

**Solutions:**
1. Check Dockerfile path is `./Dockerfile.api`
2. Verify all environment variables are set
3. Check build logs for specific error
4. Common errors:
   - Missing `requirements.txt` → Ensure file exists
   - Python package build fails → Check `requirements.txt` versions
   - Dockerfile syntax error → Verify Dockerfile.api is correct

### Issue 2: Dashboard Shows "API Unavailable"

**Symptoms:**
- Dashboard loads but shows red "API Unavailable" badge
- KPI cards show "N/A"

**Solutions:**
1. **Check `BACKEND_API_URL` is set:**
   - Go to dashboard service → Environment tab
   - Verify `BACKEND_API_URL` exists
   - Value should be: `https://smartphone-intelligence-api.onrender.com` (your actual URL)

2. **Verify backend is running:**
   - Open backend URL in browser
   - Test `/health` endpoint
   - Check backend service status in Render

3. **Check backend URL format:**
   - Must start with `https://`
   - Must end with `.onrender.com`
   - No trailing slash
   - Example: `https://smartphone-intelligence-api.onrender.com`

### Issue 3: Snowflake Connection Errors

**Symptoms:**
- Backend health check shows Snowflake as "disconnected"
- API endpoints return 500 errors

**Solutions:**
1. **Verify Snowflake credentials:**
   - Check all Snowflake env vars are set correctly
   - Account format: `ORG-ACCOUNT` (e.g., `MOPRGFY-EE19523`)
   - Password doesn't have extra spaces

2. **Test credentials locally:**
   - Run backend locally with same credentials
   - Verify Snowflake connection works

3. **Check Snowflake permissions:**
   - User has access to database
   - Warehouse is running
   - Role has necessary permissions

### Issue 4: Dashboard Shows Localhost URLs

**Symptoms:**
- API status shows `http://127.0.0.1:8000` or `localhost:8000`
- Sidebar shows localhost URL

**Solutions:**
1. **Verify `BACKEND_API_URL` is set:**
   - Dashboard service → Environment tab
   - Must be set to Render backend URL

2. **Redeploy dashboard:**
   - After setting `BACKEND_API_URL`, service should auto-redeploy
   - Or manually trigger redeploy

3. **Clear browser cache:**
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### Issue 5: Services Spin Down (Free Tier)

**Symptoms:**
- First request takes 30+ seconds
- Service shows "Sleeping" status

**Solutions:**
- This is normal for free tier
- Services wake up automatically on first request
- Consider upgrading to paid tier for always-on

---

## 📊 Verification Checklist

After deployment, verify everything works:

- [ ] Backend service shows "Live" status
- [ ] Backend `/health` returns `{"status": "healthy"}`
- [ ] Backend `/docs` shows API documentation
- [ ] Dashboard service shows "Live" status
- [ ] Dashboard loads without errors
- [ ] Dashboard shows "✅ API Available" badge
- [ ] API URL in dashboard is Render URL (not localhost)
- [ ] KPI cards show values (not N/A)
- [ ] GDP chart renders
- [ ] Revenue chart renders
- [ ] Forecast chart renders
- [ ] No localhost references anywhere
- [ ] Download buttons work
- [ ] Sidebar shows correct API URL

---

## 🎉 Success!

If all checks pass, your deployment is successful!

**Your live URLs:**
- Backend: `https://smartphone-intelligence-api.onrender.com`
- Dashboard: `https://smartphone-intelligence-dashboard.onrender.com`

**Next steps:**
1. Share dashboard URL with users
2. Monitor logs for any issues
3. Set up custom domain (optional, paid feature)
4. Consider upgrading to paid tier for better performance

---

## 📞 Need Help?

If you encounter issues:

1. **Check Render logs:**
   - Service → Logs tab
   - Look for error messages

2. **Check service status:**
   - Verify both services show "Live"
   - Check health endpoints

3. **Verify environment variables:**
   - Service → Environment tab
   - Ensure all required vars are set

4. **Test locally first:**
   - Run services locally
   - Verify they work before deploying

---

**Congratulations! Your Smartphone Intelligence Platform is now live on Render! 🚀**
