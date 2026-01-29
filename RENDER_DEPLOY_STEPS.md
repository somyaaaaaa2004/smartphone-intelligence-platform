# Render Deployment - Step-by-Step Guide

## Prerequisites

- ✅ GitHub repository pushed (already done)
- ✅ Render account (free tier works)
- ✅ Snowflake credentials ready

---

## Step 1: Deploy FastAPI Backend

### 1.1 Create Backend Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `somyaaaaaa2004/smartphone-intelligence-platform`
4. Select the repository and click **"Connect"**

### 1.2 Configure Backend Service

**Basic Settings:**
- **Name:** `smartphone-intelligence-api`
- **Environment:** `Docker`
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Dockerfile Path:** `./Dockerfile.api`
- **Docker Context:** `.` (or leave empty)
- **Plan:** `Free`

**Advanced Settings:**
- **Health Check Path:** `/health`
- **Auto-Deploy:** `Yes` (deploys on every push to main)

### 1.3 Set Environment Variables

Click **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `PORT` | `8000` | Required |
| `ENVIRONMENT` | `production` | Required |
| `SNOWFLAKE_ACCOUNT` | `MOPRGFY-EE19523` | Your Snowflake account |
| `SNOWFLAKE_USER` | `your_username` | Your Snowflake username |
| `SNOWFLAKE_PASSWORD` | `your_password` | Your Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | `your_warehouse` | Your warehouse name |
| `SNOWFLAKE_DATABASE` | `SMARTPHONE_INTELLIGENCE_DB` | Your database name |
| `SNOWFLAKE_SCHEMA` | `PUBLIC` | Schema name |
| `SNOWFLAKE_ROLE` | `SMARTPHONE_ROLE` | Optional, if using custom role |
| `LOG_LEVEL` | `INFO` | Optional, defaults to INFO |

### 1.4 Deploy Backend

1. Click **"Create Web Service"**
2. Wait for build to complete (~5-10 minutes)
3. **Copy the service URL** (e.g., `https://smartphone-intelligence-api.onrender.com`)

### 1.5 Verify Backend

Test these URLs:
- **Root:** `https://smartphone-intelligence-api.onrender.com/`
- **Health:** `https://smartphone-intelligence-api.onrender.com/health`
- **Docs:** `https://smartphone-intelligence-api.onrender.com/docs`

Expected responses:
- Root: `{"service": "Smartphone Intelligence Platform API", "status": "running", "docs": "/docs"}`
- Health: `{"status": "healthy", "api": "running", ...}`

---

## Step 2: Deploy Streamlit Dashboard

### 2.1 Create Dashboard Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect the **SAME** GitHub repository
3. Select repository and click **"Connect"**

### 2.2 Configure Dashboard Service

**Basic Settings:**
- **Name:** `smartphone-intelligence-dashboard`
- **Environment:** `Docker`
- **Region:** Same as backend (for lower latency)
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Dockerfile Path:** `./Dockerfile`
- **Docker Context:** `.` (or leave empty)
- **Plan:** `Free`

**Advanced Settings:**
- **Health Check Path:** `/_stcore/health`
- **Auto-Deploy:** `Yes`

### 2.3 Set Environment Variables

Click **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `PORT` | `8501` | Required |
| `ENVIRONMENT` | `production` | Required |
| `BACKEND_API_URL` | `https://smartphone-intelligence-api.onrender.com` | **Use your actual backend URL from Step 1** |
| `LOG_LEVEL` | `INFO` | Optional |

**⚠️ IMPORTANT:** Replace `https://smartphone-intelligence-api.onrender.com` with your actual backend URL!

### 2.4 Deploy Dashboard

1. Click **"Create Web Service"**
2. Wait for build to complete (~5-10 minutes)
3. **Copy the dashboard URL** (e.g., `https://smartphone-intelligence-dashboard.onrender.com`)

---

## Step 3: Verify Deployment

### 3.1 Test Dashboard

1. Open dashboard URL: `https://smartphone-intelligence-dashboard.onrender.com`
2. Check for:
   - ✅ **API Available** badge at top (green)
   - ✅ KPI cards showing values (not N/A)
   - ✅ Charts rendering
   - ✅ No localhost references

### 3.2 Test API Connection

In dashboard sidebar, you should see:
- ✅ **API Available** status
- ✅ API URL showing your Render backend URL (not localhost)
- ✅ Snowflake connection status (if API is connected)

### 3.3 Verify No Localhost

- Check browser console (F12) - no localhost errors
- Check dashboard source - no hardcoded localhost URLs
- API status should show Render URL

---

## Step 4: Using render.yaml (Alternative Method)

If you prefer to use `render.yaml` for automated setup:

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will detect `render.yaml` automatically
4. Review and create services
5. **Still need to set environment variables manually** in Render dashboard

---

## Troubleshooting

### Backend Issues

**Build fails:**
- Check Dockerfile.api exists
- Verify Python 3.11 is used
- Check build logs for specific errors

**Health check fails:**
- Verify `/health` endpoint works locally
- Check Snowflake credentials are correct
- Review logs in Render dashboard

**Snowflake connection errors:**
- Verify all Snowflake env vars are set
- Check account format (ORG-ACCOUNT)
- Test credentials locally first

### Dashboard Issues

**API Unavailable:**
- Verify `BACKEND_API_URL` is set correctly
- Check backend service is running
- Test backend URL directly in browser

**Charts not loading:**
- Check browser console for errors
- Verify fallback data is working (should show cached data badges)
- Check API logs for errors

**Build fails:**
- Check Dockerfile exists
- Verify requirements.txt is correct
- Check build logs for Python package errors

---

## Service URLs

After deployment, you'll have:

- **Backend API:** `https://smartphone-intelligence-api.onrender.com`
- **Dashboard:** `https://smartphone-intelligence-dashboard.onrender.com`

---

## Free Tier Limitations

- ⚠️ Services spin down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30 seconds
- ⚠️ Limited build minutes per month
- 💡 Consider upgrading for production use

---

## Next Steps

1. ✅ Test all endpoints
2. ✅ Verify data loads correctly
3. ✅ Monitor logs for errors
4. ✅ Set up custom domain (optional)
5. ✅ Configure auto-scaling (paid tier)

---

**Deployment Complete!** 🎉

Your app is now live on Render:
- Backend: `https://smartphone-intelligence-api.onrender.com`
- Dashboard: `https://smartphone-intelligence-dashboard.onrender.com`
