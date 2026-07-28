# 📱 Smartphone Intelligence Platform

A full-stack analytics project comparing **Apple vs Samsung** performance alongside macro-economic indicators (GDP, inflation, population) for India and Brazil, built with a real ETL pipeline, a Snowflake warehouse, a FastAPI backend, and an interactive Streamlit dashboard.

🔗 **Live Dashboard:** https://smartphone-intelligence-platform.streamlit.app/
🔗 **Backend API:** https://smartphone-intelligence-dashboard.onrender.com/
🔗 **Repo:** https://github.com/somyaaaaaa2004/smartphone-intelligence-platform

![Dashboard Preview](assets/dashboard.png)

---

## 🔑 Key Insights
<!-- TODO: replace these with your actual findings — this section matters more than the tech stack for analyst roles -->
- [e.g. "Apple's market share in India grew from X% to Y% between 2015–2024, while Samsung's declined by Z%"]
- [e.g. "GDP growth in Brazil correlates with a N% increase in premium smartphone revenue share"]
- [e.g. "ARIMA forecasts project Apple revenue reaching $X by 2029, a Y% CAGR"]

*(Swap these placeholders for 2–3 real numbers pulled from your dashboard — this is the single highest-impact edit you can make to this README.)*

---

## 🚀 What This Project Does

This is a learning/portfolio project that builds a small but complete analytics pipeline end to end:

- **Data Engineering**: ingests company financial data and World Bank macro indicators, loads them through MySQL into a Snowflake warehouse
- **Backend**: FastAPI service reading from Snowflake, with health checks and parameterized queries
- **Analytics & Forecasting**: revenue/net income trends, YoY growth, CAGR, market share, and 5-year forecasts using ARIMA and linear regression
- **Dashboard**: Streamlit + Plotly, with filters for company, year range, forecast model, and metric

**Scope, honestly stated:** 2 companies (Apple, Samsung), 2 countries (India, Brazil), 10 years of data (2015–2024), ~200 macro indicator rows. This is a compact dataset built to demonstrate the full pipeline pattern — not a production quant research system — and the value here is in the engineering (pipeline → warehouse → API → dashboard), not the size of the dataset.

---

## 📊 Data Sources
<!-- TODO: fill in exactly where the Apple/Samsung financial figures come from — 10-K filings? Macrotrends? Manually compiled? Be specific, since World Bank API only covers macro indicators, not company financials. -->
- **Company financials (Apple, Samsung)**: [source — e.g. annual reports / Macrotrends / manually compiled CSV]
- **Macro indicators (GDP, inflation, population)**: World Bank API
- **Time range**: 2015–2024
- **Forecast horizon**: 5 years (2025–2029)

---

## 🧠 Analytics & Forecasting

**Financial analytics**
- Revenue & net income trends, YoY growth, CAGR
- Market share analysis, cumulative revenue (S-curve)

**Forecasting**
- ARIMA (time-series)
- Linear regression (trend-based)
- Model comparison via dashboard toggle

**Dashboard features**
- Line, bar, donut, and stacked area charts
- CSV export, KPI cards, dark/light mode
- Filters: company, year range, forecast model, metric

---

## 🔌 Backend API (FastAPI)

| Endpoint | Description |
|---|---|
| `/health` | API & Snowflake connectivity check |
| `/macro/{country_code}` | Macro indicators by country |
| `/companies` | Company financials |
| `/forecasts/{company}` | Revenue forecasts |

Snowflake is the analytics warehouse; queries are parameterized and connection health is validated on startup.

---

## 🔄 Data Pipelines

- World Bank API → MySQL
- CSV → MySQL
- MySQL → Snowflake
- CSV → Snowflake (idempotent loads)

---

## 🛠 Tech Stack

**Backend**: FastAPI, Uvicorn, Gunicorn, Snowflake Connector, python-dotenv
**Dashboard**: Streamlit, Plotly, Pandas, NumPy, scikit-learn
**Forecasting**: ARIMA (statsmodels), Linear Regression (scikit-learn)
**Databases**: Snowflake (analytics), MySQL (ingestion)
**Deployment**: Docker, Render (API), Streamlit Cloud (dashboard)

---

## ⚙️ Running Locally

```bash
git clone https://github.com/somyaaaaaa2004/smartphone-intelligence-platform
cd smartphone-intelligence-platform
pip install -r requirements.txt
# set up .env using .env.example
uvicorn backend.main:app --reload   # adjust path to your actual entrypoint
streamlit run dashboard/app.py      # adjust path to your actual entrypoint
```

---

## 🎯 What I Learned Building This

Building this project meant working through the full lifecycle of a data product, not just the modeling piece:
- Designing a warehouse schema and loading pipeline from raw API/CSV sources
- Writing a backend API layer on top of Snowflake with health checks and connection pooling
- Comparing forecasting approaches (ARIMA vs linear regression) and presenting both for comparison rather than picking one
- Deploying and debugging a multi-service app (API + dashboard) across cloud platforms — including diagnosing cold-start and connection issues in production

---

## 👤 Author
Somya Shukla Aspiring Data Analyst | Interests: financial analytics, forecasting, data engineering, dashboarding 📧 somya0318@gmail.com · LinkedIn · GitHub
**Somya Shukla**
Aspiring Data Analyst | Interests: financial analytics, forecasting, data engineering, dashboarding
📧 somya0318@gmail.com · [LinkedIn](https://linkedin.com/in/somyashukla) · [GitHub](https://github.com/somyaaaaaa2004)
