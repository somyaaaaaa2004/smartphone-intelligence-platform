# Render Deployment - Quick Start Guide

**For detailed instructions, see `RENDER_DETAILED_STEPS.md`**

---

## 🚀 Quick Deployment Steps

### 1️⃣ Deploy Backend (5 minutes)

1. Go to https://dashboard.render.com → **"New +"** → **"Web Service"**
2. Connect repo: `somyaaaaaa2004/smartphone-intelligence-platform`
3. Configure:
   ```
   Name: smartphone-intelligence-api
   Dockerfile: ./Dockerfile.api
   Plan: Free
   ```
4. Set environment variables:
   ```
   PORT=8000
   ENVIRONMENT=production
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=PUBLIC
   ```
5. Click **"Create Web Service"**
6. **Wait for "Live"** → Copy backend URL

### 2️⃣ Deploy Dashboard (5 minutes)

1. **"New +"** → **"Web Service"** (same repo)
2. Configure:
   ```
   Name: smartphone-intelligence-dashboard
   Dockerfile: ./Dockerfile
   Plan: Free
   ```
3. Set environment variables:
   ```
   PORT=8501
   ENVIRONMENT=production
   BACKEND_API_URL=https://smartphone-intelligence-api.onrender.com
   ```
   ⚠️ **Replace with YOUR backend URL from step 1!**
4. Click **"Create Web Service"**
5. **Wait for "Live"** → Copy dashboard URL

### 3️⃣ Verify (2 minutes)

1. Open dashboard URL
2. Check for:
   - ✅ "API Available" badge (green)
   - ✅ KPI cards with values
   - ✅ Charts rendering
   - ✅ No localhost URLs

---

## 📋 Environment Variables Cheat Sheet

### Backend Service
```bash
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
SNOWFLAKE_ACCOUNT=MOPRGFY-EE19523
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=SMARTPHONE_INTELLIGENCE_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=SMARTPHONE_ROLE  # Optional
```

### Dashboard Service
```bash
PORT=8501
ENVIRONMENT=production
LOG_LEVEL=INFO
BACKEND_API_URL=https://smartphone-intelligence-api.onrender.com
```

---

## 🔍 Quick Verification

```bash
# Test backend
curl https://smartphone-intelligence-api.onrender.com/health

# Test dashboard
curl https://smartphone-intelligence-dashboard.onrender.com/_stcore/health
```

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Forgetting to set `BACKEND_API_URL`** → Dashboard won't connect
2. ❌ **Using wrong Dockerfile** → Backend needs `./Dockerfile.api`, Dashboard needs `./Dockerfile`
3. ❌ **Wrong Snowflake account format** → Use `ORG-ACCOUNT` format
4. ❌ **Deploying dashboard before backend** → Need backend URL first
5. ❌ **Typo in environment variable names** → Case-sensitive!

---

## 📚 Full Documentation

- **Detailed Steps:** `RENDER_DETAILED_STEPS.md` (complete walkthrough)
- **Deployment Summary:** `DEPLOYMENT_SUMMARY.md`
- **Environment Variables:** `RENDER_ENV_VARIABLES.md`

---

**Need help?** See `RENDER_DETAILED_STEPS.md` for complete instructions with troubleshooting.
