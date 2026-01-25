# 📱 Smartphone Intelligence Platform

A comprehensive data intelligence platform for analyzing smartphone market trends, macroeconomic indicators, and company financials with AI-powered forecasting.

## ✨ Features

- **📊 Interactive Dashboard**: Real-time Streamlit dashboard with interactive charts
- **🔌 RESTful API**: FastAPI backend with Snowflake integration
- **📈 Forecasting**: ML-powered revenue forecasting using Linear Regression and ARIMA
- **☁️ Cloud-Ready**: Production-ready with Gunicorn, health checks, and deployment configs
- **🔒 Secure**: Environment-based configuration, no credential logging

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Snowflake account (for data storage)
- MySQL (optional, for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd smartphone-intelligence-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Snowflake credentials
   ```

5. **Start FastAPI server**
   ```bash
   python -m uvicorn backend.main:app --port 8000
   ```

6. **Start Streamlit dashboard** (in another terminal)
   ```bash
   streamlit run dashboard/app.py
   ```

## 🌐 Live Deployment

### Deploy to Railway (Recommended)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Connect your GitHub repository
4. Add environment variables
5. Deploy! 🚀

**Your live link**: `https://your-app-name.up.railway.app`

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📁 Project Structure

```
smartphone-intelligence-platform/
├── backend/              # FastAPI application
│   └── main.py          # Main API server
├── dashboard/           # Streamlit dashboard
│   └── app.py           # Dashboard application
├── pipeline/            # Data pipelines
│   ├── db_snowflake.py  # Snowflake connection
│   ├── db_mysql.py      # MySQL connection
│   └── ...              # Data ingestion scripts
├── forecasting/         # ML forecasting
│   └── run_forecasts.py # Forecast generation
├── data/                # Data files
├── database/            # Database schemas
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container configuration
└── gunicorn.conf.py     # Production server config
```

## 🔌 API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /macro/{country_code}` - Get macro indicators
- `GET /companies` - Get company financials
- `GET /forecasts/{company}` - Get forecasts
- `GET /docs` - API documentation (Swagger UI)

## 🛠️ Development

### Run Pipelines

```bash
# Load World Bank data to MySQL
python -m pipeline.worldbank_to_mysql

# Load company financials to MySQL
python -m pipeline.load_company_financials

# Migrate MySQL to Snowflake
python -m pipeline.mysql_to_snowflake

# Load CSV to Snowflake
python -m pipeline.csv_to_snowflake

# Generate forecasts
python -m forecasting.run_forecasts
```

### Verify Setup

```bash
python verify_setup.py
```

## 📊 Dashboard Features

- **KPI Cards**: Latest GDP and revenue metrics
- **Macro Indicators**: GDP, Population, Inflation comparisons
- **Revenue Charts**: Apple vs Samsung revenue trends
- **Forecasts**: 5-year revenue projections
- **Data Export**: Download chart data as CSV

## 🔒 Security

- ✅ Environment variables for sensitive data
- ✅ No credential logging
- ✅ Parameterized SQL queries
- ✅ Error message sanitization
- ✅ Production-ready configuration

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment instructions
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Production setup
- [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md) - Local setup guide
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - System health report

## 🧪 Testing

```bash
# Test API health
curl http://localhost:8000/health

# Test endpoints
curl http://localhost:8000/macro/IND
curl http://localhost:8000/companies
curl http://localhost:8000/forecasts/Apple
```

## 🐛 Troubleshooting

See [SYSTEM_STATUS.md](SYSTEM_STATUS.md) for known issues and solutions.

## 📝 License

This project is for educational/demonstration purposes.

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Built with**: FastAPI, Streamlit, Snowflake, Python 3.13
