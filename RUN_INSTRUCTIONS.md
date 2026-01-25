# Smartphone Intelligence Platform - Run Instructions

Complete step-by-step guide to run the project on Windows PowerShell.

## Prerequisites

- Python 3.13 installed
- Docker Desktop installed (for MySQL)
- Git (optional, for cloning)

---

## Step 1: Navigate to Project Directory

Open PowerShell and navigate to the project directory:

```powershell
cd "C:\Users\HP\OneDrive\Desktop\smartphone-intelligence-platform"
```

---

## Step 2: Create and Activate Virtual Environment

### Create virtual environment (if not already created):

```powershell
python -m venv .venv
```

### Activate virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(.venv)` prefix in your PowerShell prompt.

---

## Step 3: Upgrade pip, setuptools, and wheel

Ensure you have the latest build tools:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

---

## Step 4: Install Dependencies

Install all required packages from `requirements.txt`:

```powershell
pip install --only-binary :all: -r requirements.txt
```

**Alternative (if above fails):**
```powershell
pip install -r requirements.txt
```

Wait for installation to complete. This may take a few minutes.

---

## Step 5: Configure Environment Variables

### Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

### Edit `.env` file with your actual credentials:

Open `.env` in a text editor and fill in:
- MySQL credentials (host, port, database, user, password)
- Snowflake credentials (account, user, password, warehouse, database, schema)

**Important:** Never commit `.env` to version control!

---

## Step 6: Start MySQL Database (Docker)

### Start MySQL container:

```powershell
docker compose up -d
```

### Verify MySQL is running:

```powershell
docker ps
```

You should see `smartphone_mysql` container running.

### Apply database schema (if not already applied):

```powershell
Get-Content database\schema.sql | docker exec -i smartphone_mysql mysql -uroot -prootpassword smartphone_intelligence
```

### Verify tables exist:

```powershell
docker exec -it smartphone_mysql mysql -uroot -prootpassword -e "USE smartphone_intelligence; SHOW TABLES;"
```

---

## Step 7: Load Initial Data (Optional)

### Load World Bank data into MySQL:

```powershell
python -m pipeline.worldbank_to_mysql
```

### Load company financials:

```powershell
python -m pipeline.load_company_financials
```

### Generate forecasts:

```powershell
python -m forecasting.run_forecasts
```

---

## Step 8: Start FastAPI Backend

### Open a NEW PowerShell window (keep the first one for later)

Navigate to project directory and activate venv:

```powershell
cd "C:\Users\HP\OneDrive\Desktop\smartphone-intelligence-platform"
.\.venv\Scripts\Activate.ps1
```

### Start FastAPI server:

```powershell
uvicorn backend.main:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Environment variables validated successfully
✓ MySQL connection configured
INFO:     Application startup complete.
```

**Keep this window open!** The API server must stay running.

---

## Step 9: Start Streamlit Dashboard

### Open a THIRD PowerShell window

Navigate to project directory and activate venv:

```powershell
cd "C:\Users\HP\OneDrive\Desktop\smartphone-intelligence-platform"
.\.venv\Scripts\Activate.ps1
```

### Start Streamlit dashboard:

```powershell
streamlit run dashboard/app.py --server.port 8501
```

You should see output like:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Keep this window open!** The dashboard must stay running.

---

## Step 10: Verify Endpoints in Browser

### FastAPI Endpoints:

1. **Root endpoint (Welcome message):**
   ```
   http://127.0.0.1:8000/
   ```

2. **Health check:**
   ```
   http://127.0.0.1:8000/health
   ```

3. **Interactive API documentation:**
   ```
   http://127.0.0.1:8000/docs
   ```

4. **Alternative API documentation:**
   ```
   http://127.0.0.1:8000/redoc
   ```

5. **Macro indicators (India):**
   ```
   http://127.0.0.1:8000/snowflake/macro/IND
   ```

6. **Macro indicators (Brazil):**
   ```
   http://127.0.0.1:8000/snowflake/macro/BRA
   ```

7. **Company financials:**
   ```
   http://127.0.0.1:8000/snowflake/companies
   ```

8. **Forecasts (Apple):**
   ```
   http://127.0.0.1:8000/snowflake/forecasts/Apple
   ```

9. **Forecasts (Samsung):**
   ```
   http://127.0.0.1:8000/snowflake/forecasts/Samsung
   ```

### Streamlit Dashboard:

Open in your browser:
```
http://localhost:8501
```

You should see:
- KPI cards at the top
- Comparative analysis charts
- Revenue forecasts section
- Sidebar with settings

---

## Quick Reference: All Commands in Order

```powershell
# 1. Navigate to project
cd "C:\Users\HP\OneDrive\Desktop\smartphone-intelligence-platform"

# 2. Activate venv
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip (if needed)
python -m pip install --upgrade pip setuptools wheel

# 4. Install dependencies
pip install --only-binary :all: -r requirements.txt

# 5. Start MySQL (in first terminal)
docker compose up -d

# 6. Apply schema (if needed)
Get-Content database\schema.sql | docker exec -i smartphone_mysql mysql -uroot -prootpassword smartphone_intelligence

# 7. Load data (optional)
python -m pipeline.worldbank_to_mysql
python -m pipeline.load_company_financials
python -m forecasting.run_forecasts

# 8. Start FastAPI (in second terminal)
uvicorn backend.main:app --reload --port 8000

# 9. Start Streamlit (in third terminal)
streamlit run dashboard/app.py --server.port 8501
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError" when running scripts

**Solution:** Ensure virtual environment is activated:
```powershell
.\.venv\Scripts\Activate.ps1
```

### Issue: "Port 8000 already in use"

**Solution:** Find and kill the process:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### Issue: "Port 8501 already in use"

**Solution:** Use a different port:
```powershell
streamlit run dashboard/app.py --server.port 8502
```

### Issue: "MySQL connection failed"

**Solution:** 
1. Check MySQL container is running: `docker ps`
2. Verify credentials in `.env` match `docker-compose.yml`
3. Restart MySQL: `docker compose restart mysql`

### Issue: "Snowflake connection failed"

**Solution:**
1. Verify all Snowflake credentials in `.env`
2. Check account format (ORG-ACCOUNT or ACCOUNT.REGION.CLOUD)
3. Ensure role is granted (see `database/ROLE_SETUP_INSTRUCTIONS.md`)

### Issue: "Environment variables not found"

**Solution:**
1. Ensure `.env` file exists in project root
2. Copy from `.env.example` if missing
3. Fill in all required values

---

## Stopping Services

### Stop Streamlit:
Press `Ctrl+C` in the Streamlit terminal window

### Stop FastAPI:
Press `Ctrl+C` in the FastAPI terminal window

### Stop MySQL:
```powershell
docker compose down
```

### Deactivate virtual environment:
```powershell
deactivate
```

---

## Project Structure

```
smartphone-intelligence-platform/
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example            # Environment template
├── requirements.txt         # Python dependencies
├── docker-compose.yml      # MySQL Docker setup
├── backend/
│   └── main.py            # FastAPI application
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── pipeline/
│   ├── db_mysql.py        # MySQL connection
│   ├── db_snowflake.py    # Snowflake connection
│   ├── worldbank_to_mysql.py
│   ├── load_company_financials.py
│   └── mysql_to_snowflake.py
├── forecasting/
│   └── run_forecasts.py
└── database/
    ├── schema.sql          # MySQL schema
    └── snowflake_*.sql     # Snowflake setup scripts
```

---

## Next Steps

1. **Load data into MySQL:**
   - Run `python -m pipeline.worldbank_to_mysql`
   - Run `python -m pipeline.load_company_financials`

2. **Generate forecasts:**
   - Run `python -m forecasting.run_forecasts`

3. **Sync to Snowflake:**
   - Run `python -m pipeline.mysql_to_snowflake`

4. **Access dashboard:**
   - Open `http://localhost:8501` in your browser

---

## Support

For issues or questions:
- Check error messages in terminal output
- Verify all environment variables are set correctly
- Ensure MySQL and Snowflake connections are working
- Review logs for detailed error information
