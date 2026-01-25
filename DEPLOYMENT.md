# Deployment Guide

This document outlines the deployment-ready configuration for the Smartphone Intelligence Platform.

## Deployment-Ready Features

### 1. Environment Configuration
- ✅ `.env.example` includes all required variables
- ✅ `.gitignore` excludes sensitive files (`.env`, `.venv`, `__pycache__`)
- ✅ Environment variable validation on startup

### 2. Backend (FastAPI) Configuration
- ✅ Configurable host via `API_HOST` (default: `0.0.0.0`)
- ✅ Configurable port via `PORT` (default: `8000`)
- ✅ Auto-reload disabled in production (via `ENVIRONMENT` variable)
- ✅ Runs on `0.0.0.0` for container/cloud deployment

### 3. Dashboard (Streamlit) Configuration
- ✅ Configurable API URL via `API_URL` environment variable
- ✅ Defaults to `http://localhost:8000` for local development
- ✅ Can be set to production API URL for deployment

## Environment Variables

### Required for Backend:
```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_DB=smartphone_intelligence
MYSQL_USER=app_user
MYSQL_PASSWORD=your_password

# Snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=  # Optional

# Server (Optional)
PORT=8000
API_HOST=0.0.0.0
ENVIRONMENT=production  # Set to 'development' for auto-reload
```

### Required for Dashboard:
```env
# API Connection
API_URL=http://localhost:8000  # Set to production URL in deployment
```

## Deployment Commands

### Backend (FastAPI):
```powershell
# Development
uvicorn backend.main:app --reload --port 8000

# Production (uses PORT env var)
uvicorn backend.main:app --host 0.0.0.0 --port $env:PORT
```

### Dashboard (Streamlit):
```powershell
# Development
streamlit run dashboard/app.py --server.port 8501

# Production (with API_URL set)
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

## Cloud Deployment Examples

### Heroku:
```bash
# Set environment variables
heroku config:set PORT=8000
heroku config:set API_URL=https://your-api.herokuapp.com

# Deploy
git push heroku main
```

### Docker:
```dockerfile
# Example Dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables in Docker:
```yaml
# docker-compose.yml example
services:
  api:
    environment:
      - PORT=8000
      - API_HOST=0.0.0.0
      - ENVIRONMENT=production
  dashboard:
    environment:
      - API_URL=http://api:8000
```

## Security Checklist

- ✅ `.env` excluded from git
- ✅ Passwords never logged
- ✅ Environment validation on startup
- ✅ `.gitignore` properly configured

## Production Considerations

1. **Set `ENVIRONMENT=production`** to disable auto-reload
2. **Use HTTPS** in production (configure reverse proxy)
3. **Set strong passwords** in production `.env`
4. **Configure CORS** if needed for cross-origin requests
5. **Use environment-specific `.env` files** (`.env.production`, `.env.staging`)
