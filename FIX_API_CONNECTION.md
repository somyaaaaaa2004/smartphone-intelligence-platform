# Fix API Unavailable Issue - Step-by-Step Guide

## 🔍 Problem

Dashboard shows:
- ❌ "API Unavailable" 
- 📊 "Using cached data — API unavailable"
- API Configuration shows URL but connection fails

## ✅ Solution Steps

### Step 1: Verify Backend Service is Running

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Find your backend service: **`smartphone-intelligence-api`**
3. Check status:
   - ✅ Should show **"Live"** (green)
   - ❌ If shows "Sleeping" or "Failed" → Fix backend first

**If backend is not Live:**
- Check build logs for errors
- Verify Snowflake credentials are correct
- Ensure all environment variables are set

### Step 2: Get Correct Backend URL

1. In Render dashboard, click on **`smartphone-intelligence-api`** service
2. Look at the top of the page
3. You'll see a URL like: `https://smartphone-intelligence-api.onrender.com`
4. **COPY THIS EXACT URL** (including `https://`)

**Example format:**
```
https://smartphone-intelligence-api.onrender.com
```

### Step 3: Test Backend URL Directly

Open these URLs in your browser to verify backend works:

**Test 1: Root endpoint**
```
https://smartphone-intelligence-api.onrender.com/
```
**Expected:** `{"service": "Smartphone Intelligence Platform API", "status": "running", "docs": "/docs"}`

**Test 2: Health endpoint**
```
https://smartphone-intelligence-api.onrender.com/health
```
**Expected:** `{"status": "healthy", "api": "running", ...}`

**If these don't work:**
- Backend is not running → Fix backend deployment first
- Check backend logs in Render dashboard

### Step 4: Set BACKEND_API_URL in Dashboard Service

1. In Render dashboard, click on **`smartphone-intelligence-dashboard`** service
2. Click **"Environment"** tab (left sidebar)
3. Look for `BACKEND_API_URL` variable:
   - **If it exists:** Click on it → Edit → Update value
   - **If it doesn't exist:** Click **"Add Environment Variable"**

4. Set the variable:
   - **Key:** `BACKEND_API_URL`
   - **Value:** `https://smartphone-intelligence-api.onrender.com`
     - ⚠️ **Use YOUR actual backend URL from Step 2!**
     - Must start with `https://`
     - Must end with `.onrender.com`
     - **NO trailing slash** (don't add `/` at the end)

5. Click **"Save Changes"**

**Example:**
```
Key: BACKEND_API_URL
Value: https://smartphone-intelligence-api.onrender.com
```

### Step 5: Verify Environment Variable

After saving, verify it's set correctly:

1. In dashboard service → Environment tab
2. You should see:
   ```
   BACKEND_API_URL = https://smartphone-intelligence-api.onrender.com
   ```
3. Check:
   - ✅ Value matches your backend URL exactly
   - ✅ No extra spaces before/after
   - ✅ Starts with `https://`
   - ✅ No trailing slash

### Step 6: Redeploy Dashboard

After setting `BACKEND_API_URL`, Render should auto-redeploy. If not:

1. Go to dashboard service page
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Wait for deployment to complete (~5 minutes)
4. Status should show **"Live"**

### Step 7: Verify Fix

1. Open dashboard URL: `https://smartphone-intelligence-dashboard.onrender.com`
2. Wait for page to load (may take 30 seconds on first load)
3. Check for:
   - ✅ **"✅ API Available"** badge at top (green)
   - ✅ API URL in sidebar shows your Render backend URL
   - ✅ KPI cards show values (not "N/A")
   - ✅ Charts load with live data (not just cached)

### Step 8: Clear Browser Cache (If Still Not Working)

Sometimes browser cache causes issues:

1. **Hard refresh:** Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
2. **Or clear cache:**
   - Press `F12` → Application tab → Clear storage → Clear site data
   - Refresh page

---

## 🔧 Common Issues & Solutions

### Issue 1: BACKEND_API_URL Not Set

**Symptom:** Dashboard shows default URL (`http://127.0.0.1:8000`)

**Solution:**
- Follow Step 4 above
- Ensure variable name is exactly `BACKEND_API_URL` (case-sensitive)

### Issue 2: Wrong Backend URL Format

**Symptom:** Connection still fails after setting variable

**Check:**
- ✅ URL starts with `https://` (not `http://`)
- ✅ URL ends with `.onrender.com` (not `.com/` or other)
- ✅ No trailing slash
- ✅ Matches backend service URL exactly

**Wrong examples:**
```
❌ http://smartphone-intelligence-api.onrender.com  (http instead of https)
❌ https://smartphone-intelligence-api.onrender.com/  (trailing slash)
❌ smartphone-intelligence-api.onrender.com  (missing https://)
```

**Correct:**
```
✅ https://smartphone-intelligence-api.onrender.com
```

### Issue 3: Backend Service Not Running

**Symptom:** Backend URL doesn't respond

**Solution:**
1. Check backend service status in Render
2. Verify backend shows "Live"
3. Test backend URL directly in browser
4. Check backend logs for errors

### Issue 4: CORS or Network Issues

**Symptom:** Connection timeout or CORS errors

**Solution:**
- Backend should allow CORS (already configured)
- Check backend logs for CORS errors
- Verify both services are in same region

### Issue 5: Environment Variable Not Applied

**Symptom:** Variable is set but dashboard still uses old URL

**Solution:**
1. Verify variable is saved (Step 5)
2. Manually trigger redeploy (Step 6)
3. Wait for deployment to complete
4. Hard refresh browser

---

## 📋 Quick Checklist

Use this checklist to verify everything:

- [ ] Backend service shows "Live" status
- [ ] Backend URL works: `https://your-backend.onrender.com/health`
- [ ] `BACKEND_API_URL` is set in dashboard service
- [ ] `BACKEND_API_URL` value matches backend URL exactly
- [ ] `BACKEND_API_URL` starts with `https://`
- [ ] `BACKEND_API_URL` has no trailing slash
- [ ] Dashboard service redeployed after setting variable
- [ ] Dashboard shows "✅ API Available" (green badge)
- [ ] No localhost URLs visible
- [ ] KPI cards show values (not N/A)

---

## 🎯 Expected Result

After fixing, you should see:

**Top of Dashboard:**
- ✅ **"API Available"** (green badge)
- API URL shows: `https://smartphone-intelligence-api.onrender.com`

**Sidebar:**
- API Configuration shows Render backend URL
- No localhost references

**Charts:**
- Load with live data from API
- May show "Live data from API" tooltips
- No "Using cached data" warnings (unless API is actually down)

---

## 🆘 Still Not Working?

If issue persists after following all steps:

1. **Check Render Logs:**
   - Dashboard service → Logs tab
   - Look for errors related to API connection
   - Check for environment variable loading errors

2. **Verify Backend:**
   - Test backend URL directly: `curl https://your-backend.onrender.com/health`
   - Check backend logs for connection attempts

3. **Test Locally:**
   - Set `BACKEND_API_URL` locally
   - Run dashboard: `streamlit run dashboard/app.py`
   - Verify connection works locally

4. **Contact Support:**
   - Render support: https://render.com/docs/support
   - Check Render status page for outages

---

**Follow these steps in order, and your API connection should work!** 🚀
