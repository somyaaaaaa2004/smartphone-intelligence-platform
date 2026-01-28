# Render Environment Variables - Complete List

You need **TWO services** on Render. Each has different environment variables.

---

## Service 1: FastAPI Backend (`smartphone-intelligence-api`)

**Dockerfile:** `Dockerfile.api`

| Variable Name | Example Value | Required |
|--------------|---------------|----------|
| `PORT` | `8000` | Yes |
| `ENVIRONMENT` | `production` | Yes |
| `SNOWFLAKE_ACCOUNT` | `MOPRGFY-EE19523` | Yes |
| `SNOWFLAKE_USER` | `SMARTPHONE_USER` | Yes |
| `SNOWFLAKE_PASSWORD` | `YourPassword123!` | Yes |
| `SNOWFLAKE_WAREHOUSE` | `SMARTPHONE_WH` | Yes |
| `SNOWFLAKE_DATABASE` | `SMARTPHONE_INTELLIGENCE_DB` | Yes |
| `SNOWFLAKE_SCHEMA` | `PUBLIC` | Yes |
| `SNOWFLAKE_ROLE` | `SMARTPHONE_ROLE` | Optional |

---

## Service 2: Streamlit Dashboard (`smartphone-intelligence-dashboard`)

**Dockerfile:** `Dockerfile`

| Variable Name | Example Value | Required |
|--------------|---------------|----------|
| `PORT` | `8501` | Yes |
| `ENVIRONMENT` | `production` | Yes |
| `BACKEND_API_URL` | `https://smartphone-intelligence-api.onrender.com` | **Yes** |

**Important:** The `BACKEND_API_URL` must point to your deployed API service URL!

---

## How to Set in Render Dashboard

1. Go to your Render dashboard
2. Click on your service
3. Go to **"Environment"** tab
4. Click **"Add Environment Variable"**
5. Enter the variable name and value
6. Click **"Save Changes"**

Render will automatically redeploy after saving.

---

## Deployment Order

1. **Deploy API first** → Get the URL (e.g., `https://smartphone-intelligence-api.onrender.com`)
2. **Deploy Dashboard second** → Set `API_URL` to the API URL from step 1
