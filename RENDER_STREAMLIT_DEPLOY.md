# 🚀 Deploy Streamlit Dashboard on Render

## Quick Deploy Guide

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render Streamlit deployment"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to Render**: https://render.com
2. **Sign up/Login** with GitHub
3. **Click "New"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Configure**:
   - **Name**: `smartphone-intelligence-dashboard`
   - **Environment**: `Docker` (important!)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile` (or leave empty if in root)
   - **Docker Context**: `.` (root directory)

6. **Add Environment Variables**:
   In Render dashboard → Environment tab, add:
   ```
   PORT=8501
   ENVIRONMENT=production
   API_URL=https://your-api-url.onrender.com (or http://localhost:8000 if API is on same service)
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=PUBLIC
   ```

7. **Deploy!**
   - Click **"Create Web Service"**
   - Render will build and deploy automatically
   - **Your live link**: `https://smartphone-intelligence-dashboard.onrender.com`

## ✅ What's Fixed

1. **Build Tools**: Added `gcc`, `g++`, `build-essential` for `snowflake-connector-python`
2. **Streamlit Command**: Properly configured with `--server.port` and `--server.address`
3. **Port Configuration**: Uses `$PORT` from Render environment
4. **Health Check**: Streamlit-specific health check endpoint

## 🧪 Test Your Deployment

After deployment:
```
https://smartphone-intelligence-dashboard.onrender.com
```

## 📝 Important Notes

1. **Free Tier**: App spins down after 15 min inactivity (first request may be slow)
2. **API URL**: Update `API_URL` environment variable to point to your deployed API
3. **Port**: Render sets `PORT` automatically, Streamlit uses it via `--server.port=$PORT`

## 🔧 Troubleshooting

**Build fails with g++ error?**
- ✅ Fixed! Dockerfile now includes `g++` and `build-essential`

**Streamlit not accessible?**
- Check `--server.address=0.0.0.0` is set (it is in Dockerfile)
- Verify PORT environment variable is set in Render

**Dashboard can't connect to API?**
- Update `API_URL` in Render environment variables
- Ensure API is deployed and accessible

---

**Your live Streamlit dashboard**: `https://smartphone-intelligence-dashboard.onrender.com` 🎉
