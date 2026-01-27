# Render Deployment Guide - Complete Setup

Your project requires **TWO separate services** on Render:

1. **FastAPI Backend** (API) - connects to Snowflake
2. **Streamlit Dashboard** (Frontend) - connects to the API

## Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Production deployment fixes"
git push
```

## Step 2: Deploy the FastAPI Backend (FIRST)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `smartphone-intelligence-api`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile.api`
   - **Plan:** Free

5. **Add Environment Variables** (in Render dashboard):

| Variable | Value |
|----------|-------|
| `PORT` | `8000` |
| `ENVIRONMENT` | `production` |
| `SNOWFLAKE_ACCOUNT` | `MOPRGFY-EE19523` (your account) |
| `SNOWFLAKE_USER` | `your_username` |
| `SNOWFLAKE_PASSWORD` | `your_password` |
| `SNOWFLAKE_WAREHOUSE` | `your_warehouse` |
| `SNOWFLAKE_DATABASE` | `SMARTPHONE_INTELLIGENCE_DB` |
| `SNOWFLAKE_SCHEMA` | `PUBLIC` |
| `SNOWFLAKE_ROLE` | `SMARTPHONE_ROLE` (optional) |

6. Click **"Create Web Service"**
7. Wait for deployment to complete
8. **Copy the API URL** (e.g., `https://smartphone-intelligence-api.onrender.com`)

## Step 3: Test the API

Visit these URLs in your browser:
- `https://smartphone-intelligence-api.onrender.com/` → Should show welcome JSON
- `https://smartphone-intelligence-api.onrender.com/health` → Should show health status
- `https://smartphone-intelligence-api.onrender.com/docs` → Should show API docs

## Step 4: Deploy the Streamlit Dashboard (SECOND)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect the SAME GitHub repository
4. Configure:
   - **Name:** `smartphone-intelligence-dashboard`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Free

5. **Add Environment Variables** (in Render dashboard):

| Variable | Value |
|----------|-------|
| `PORT` | `8501` |
| `ENVIRONMENT` | `production` |
| `API_URL` | `https://smartphone-intelligence-api.onrender.com` ← **YOUR API URL FROM STEP 2** |

6. Click **"Create Web Service"**
7. Wait for deployment to complete

## Step 5: Test the Dashboard

Visit your dashboard URL (e.g., `https://smartphone-intelligence-dashboard.onrender.com`)

You should see:
- ✅ API Connected in sidebar
- ✅ KPI cards with data
- ✅ Charts loading properly

---

## Quick Reference: All Environment Variables

### For API Service (`smartphone-intelligence-api`)

```
PORT=8000
ENVIRONMENT=production
SNOWFLAKE_ACCOUNT=MOPRGFY-EE19523
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=SMARTPHONE_INTELLIGENCE_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=SMARTPHONE_ROLE
```

### For Dashboard Service (`smartphone-intelligence-dashboard`)

```
PORT=8501
ENVIRONMENT=production
API_URL=https://smartphone-intelligence-api.onrender.com
```

---

## Troubleshooting

### Dashboard shows "API Not Configured"
→ Set `API_URL` environment variable in Render dashboard for the Dashboard service

### Dashboard shows "API Unavailable"
→ The API service is not running or has errors. Check API service logs in Render.

### API shows Snowflake connection errors
→ Check Snowflake credentials in API service environment variables

### Build fails with wheel errors
→ Ensure you're using the updated Dockerfiles (Python 3.11)

---

## Important Notes

- Free tier services **spin down after 15 minutes of inactivity**
- First request after spin-down takes ~30 seconds
- Consider upgrading to paid tier for always-on services
