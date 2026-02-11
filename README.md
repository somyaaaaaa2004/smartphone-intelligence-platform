# 📱 Smartphone Intelligence Platform

A **full-stack quantitative analytics platform** for analyzing **Apple vs Samsung** financial performance alongside **macro-economic indicators**, powered by **live APIs**, **Snowflake**, and **interactive dashboards**.

🔗 **Live Dashboard:** https://smartphone-intelligence-platform.streamlit.app/  
🔗 **Backend API (Render):** https://smartphone-intelligence-dashboard.onrender.com/  
🔗 **GitHub Repo:** https://github.com/somyaaaaaa2004/smartphone-intelligence-platform  
![Uploading image.png…]()

---

## 🚀 Project Overview

The Smartphone Intelligence Platform is an end-to-end analytics system that combines:

- **Data Engineering** (World Bank → MySQL → Snowflake)
- **Backend APIs** (FastAPI + Snowflake)
- **Advanced Analytics & Forecasting** (ARIMA, Linear Regression)
- **Interactive Dashboards** (Streamlit + Plotly)

It enables **10-year financial analysis**, **market share insights**, **macro comparisons**, and **multi-model forecasts** for global smartphone leaders **Apple** and **Samsung**.

---

## 📊 Key Metrics (Real Data)

| Metric | Value |
|------|------|
| Companies analyzed | **2** (Apple, Samsung) |
| Years covered | **10 years** (2015–2024) |
| Macro indicator rows | **200** |
| Countries | **2** (India, Brazil) |
| Forecast horizon | **5 years** |
| API endpoints | **10** |
| Dashboard charts | **14+** |
| Data pipelines | **4** |
| ML models | **2** (ARIMA, Linear Regression) |

---

## 🧠 Analytics & Forecasting

### Financial Analytics
- Revenue & net income trends
- YoY growth (%)
- CAGR calculation
- Market share analysis
- Cumulative revenue **S-curve**

### Forecasting
- **ARIMA** (time-series forecasting)
- **Linear Regression** (trend-based forecasting)
- 5-year revenue projections
- Model comparison via dashboard filters
- Forecasts stored and served via API

---

## 📈 Dashboard Features

### Visualizations
- **Line charts** (Revenue, Net Income, GDP, Inflation)
- **Bar charts** (YoY growth, Market share)
- **Donut charts** (Revenue share)
- **Stacked area charts**
- **S-curve (cumulative revenue)**
- **Tables** with CSV export
- **KPI cards** (latest metrics, CAGR, forecasts)

### Filters / Slicers
- Company selector (Apple / Samsung / Both)
- Year range slider
- Forecast model selector
- Metric selector (Revenue / Net Income)
- Dark / Light mode toggle
- Live API refresh button

---

## 🌍 Macro-Economic Analysis

- GDP comparison: **India vs Brazil**
- Inflation trends
- Population & GDP per capita (World Bank data)
- Macro indicators integrated into financial context

---

## 🔌 Backend API (FastAPI)

### Core Endpoints
- `/health` — API & Snowflake health check
- `/macro/{country_code}` — macro indicators
- `/companies` — company financials
- `/forecasts/{company}` — revenue forecasts

### Architecture
- Snowflake as primary analytics warehouse
- Connection pooling with health validation
- Parameterized SQL queries
- Kubernetes-style liveness & readiness probes

---

## 🔄 Data Engineering Pipelines

- **World Bank API → MySQL**
- **CSV → MySQL**
- **MySQL → Snowflake**
- **CSV → Snowflake (idempotent loads)**

All pipelines are modular, reproducible, and production-ready.

---

## 🛠 Tech Stack

**Backend**
- FastAPI, Uvicorn, Gunicorn
- Snowflake Connector
- Python-dotenv

**Dashboard**
- Streamlit
- Plotly
- Pandas, NumPy
- scikit-learn

**Forecasting**
- ARIMA (statsmodels)
- Linear Regression (scikit-learn)

**Databases**
- Snowflake (analytics + API)
- MySQL (ingestion layer)

**DevOps**
- Docker
- Render (API + Dashboard)
- Streamlit Cloud
- GitHub CI-ready structure

---

## ⚙️ Deployment

- **API** deployed on Render with Docker
- **Dashboard** deployed on Streamlit Cloud
- Auto-redeploy on GitHub commits
- Environment-based configuration
- Production health checks enabled

---

## 🎯 Why This Project Matters

This project demonstrates real-world skills in:

- Quantitative analytics
- Financial time-series modeling
- Data engineering pipelines
- API design & reliability
- Production dashboards
- Cloud deployment

It closely mirrors workflows used in **financial institutions**, **analytics teams**, and **quantitative research roles**.

---

## 👤 Author

**Somya**  
📧 Aspiring Quantitative Analytics Intern (2026)  
📊 Interests: Financial Analytics, Forecasting, Data Engineering, Visualization  

---

