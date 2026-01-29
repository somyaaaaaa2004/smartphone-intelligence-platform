# Fix Revenue Chart "API Unavailable" Issue

## 🔍 Problem

Your dashboard shows:
- ✅ **"API Available"** badge (green) - API health check passes
- ✅ API URL correctly set: `https://smartphone-intelligence-api.onrender.com`
- ❌ Revenue chart shows: **"Using cached data — API unavailable"**
- 📊 KPI cards show "Cached data" for Apple/Samsung

**This means:** The API is running, but the `/companies` endpoint is not returning data.

---

## 🔍 Diagnosis Steps

### Step 1: Test Backend `/companies` Endpoint

Open this URL in your browser:
```
https://smartphone-intelligence-api.onrender.com/companies
```

**Expected Response (Success):**
```json
{
  "count": 10,
  "data": [
    {
      "company": "Apple",
      "year": 2019,
      "revenue_usd": 260000000000,
      "net_income_usd": 55256000000
    },
    {
      "company": "Samsung",
      "year": 2019,
      "revenue_usd": 229000000000,
      ...
    }
  ]
}
```

**If you see:**
- `{"count": 0, "data": []}` → **No data in Snowflake** (see Solution 1)
- `404 Not Found` → **Endpoint doesn't exist** (check backend code)
- `500 Internal Server Error` → **Backend error** (check backend logs)
- Connection timeout → **Backend not running** (check Render dashboard)

### Step 2: Check Backend Logs

1. Go to Render Dashboard
2. Click on **`smartphone-intelligence-api`** service
3. Click **"Logs"** tab
4. Look for errors related to:
   - Snowflake connection
   - `/companies` endpoint
   - SQL queries

**Common errors:**
- `Table 'COMPANY_FINANCIALS' doesn't exist` → Table not created
- `Insufficient privileges` → Snowflake permissions issue
- `Connection timeout` → Snowflake warehouse not running

### Step 3: Verify Snowflake Data

The backend needs data in Snowflake `COMPANY_FINANCIALS` table.

**Check if data exists:**
1. Connect to Snowflake
2. Run:
```sql
SELECT COUNT(*) FROM COMPANY_FINANCIALS;
SELECT DISTINCT COMPANY FROM COMPANY_FINANCIALS;
```

**Expected:**
- Count > 0
- Companies include: `Apple`, `Samsung`

---

## ✅ Solutions

### Solution 1: Load Data into Snowflake

If the `COMPANY_FINANCIALS` table is empty:

1. **Run the data pipeline:**
   ```bash
   python -m pipeline.load_company_financials
   ```
   This loads `data/company_financials.csv` into Snowflake.

2. **Or manually insert data:**
   ```sql
   INSERT INTO COMPANY_FINANCIALS (COMPANY, YEAR, REVENUE_USD, NET_INCOME_USD)
   VALUES 
   ('Apple', 2019, 260000000000, 55256000000),
   ('Apple', 2020, 274000000000, 57411000000),
   ...
   ```

3. **Verify data loaded:**
   ```sql
   SELECT * FROM COMPANY_FINANCIALS 
   WHERE COMPANY IN ('Apple', 'Samsung')
   ORDER BY COMPANY, YEAR;
   ```

4. **Test API again:**
   - Refresh: `https://smartphone-intelligence-api.onrender.com/companies`
   - Should now return data

### Solution 2: Check Company Name Format

The dashboard expects exact company names: `Apple` and `Samsung` (case-sensitive).

**Verify in Snowflake:**
```sql
SELECT DISTINCT COMPANY FROM COMPANY_FINANCIALS;
```

**If names don't match:**
- Update data: `UPDATE COMPANY_FINANCIALS SET COMPANY = 'Apple' WHERE COMPANY = 'apple';`
- Or update dashboard code to match your data

### Solution 3: Fix Backend Endpoint

If `/companies` endpoint has errors:

1. Check backend code: `backend/main.py`
2. Verify endpoint exists: `@app.get("/companies")`
3. Check SQL query syntax
4. Verify Snowflake connection pool is working

### Solution 4: Verify Snowflake Permissions

Ensure your Snowflake user has access:

```sql
-- Check current user and role
SELECT CURRENT_USER(), CURRENT_ROLE();

-- Verify permissions
SHOW GRANTS ON TABLE COMPANY_FINANCIALS;

-- Grant if needed
GRANT SELECT ON TABLE COMPANY_FINANCIALS TO ROLE SMARTPHONE_ROLE;
```

---

## 🧪 Quick Test Script

Create a test file `test_companies_endpoint.py`:

```python
import requests
import json

api_url = "https://smartphone-intelligence-api.onrender.com"

# Test health
print("Testing /health...")
health = requests.get(f"{api_url}/health")
print(f"Status: {health.status_code}")
print(f"Response: {json.dumps(health.json(), indent=2)}")

# Test companies
print("\nTesting /companies...")
companies = requests.get(f"{api_url}/companies")
print(f"Status: {companies.status_code}")
if companies.status_code == 200:
    data = companies.json()
    print(f"Count: {data.get('count', 0)}")
    if data.get('data'):
        print(f"Companies: {set(d['company'] for d in data['data'])}")
    else:
        print("No data returned!")
else:
    print(f"Error: {companies.text}")
```

Run: `python test_companies_endpoint.py`

---

## 📋 Checklist

Use this to diagnose:

- [ ] Backend `/health` returns `{"status": "healthy"}`
- [ ] Backend `/companies` endpoint exists
- [ ] `/companies` returns `200 OK`
- [ ] `/companies` response has `count > 0`
- [ ] `/companies` data includes `Apple` and `Samsung`
- [ ] Company names match exactly (case-sensitive)
- [ ] Snowflake `COMPANY_FINANCIALS` table has data
- [ ] Snowflake user has SELECT permissions
- [ ] Backend logs show no errors

---

## 🎯 Expected Result

After fixing, when you:
1. Open dashboard
2. Check revenue chart
3. Should see: **No "Using cached data" message**
4. Chart should show live data from API
5. KPI cards should show "Live data from API" tooltip

---

## 🔧 Most Likely Cause

Based on your screenshot, the most likely issue is:

**The `/companies` endpoint is returning empty data** (`{"count": 0, "data": []}`)

**Why:**
- Backend is running (health check passes)
- But `COMPANY_FINANCIALS` table in Snowflake is empty
- Or data doesn't have Apple/Samsung companies

**Fix:**
1. Load data into Snowflake using the pipeline
2. Or manually insert test data
3. Verify with SQL query
4. Test `/companies` endpoint
5. Dashboard should update automatically

---

**Follow these steps to diagnose and fix the revenue chart API issue!** 🚀
