"""
Smartphone Intelligence Platform — Quantitative Analytics Dashboard.
Professional Bloomberg-style dashboard with dark theme.
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import time
import logging
from io import StringIO
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if os.getenv("ENVIRONMENT", "").lower() == "production":
    log_level = "INFO"
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# Page config — must be first Streamlit command
# =============================================================================
st.set_page_config(
    page_title="Smartphone Intelligence Platform",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# =============================================================================
# Theme: Dark and Light CSS (applied in main() based on toggle)
# =============================================================================
DARK_CSS = """
<style>
    .stApp { background-color: #0d1117; }
    [data-testid="stHeader"] { background: #161b22; }
    [data-testid="stToolbar"] { background: #161b22 !important; }
    [data-testid="stSidebar"] { background: #161b22; }
    [data-testid="stSidebar"] .stMarkdown { color: #c9d1d9; }
    h1, h2, h3 { color: #58a6ff !important; font-weight: 600; }
    .main-header { color: #58a6ff; font-size: 1.75rem; font-weight: 700; letter-spacing: 0.02em; margin-bottom: 0.5rem; }
    .sub-header { color: #8b949e; font-size: 0.9rem; margin-bottom: 1.5rem; }
    [data-testid="stMetricValue"] { color: #7ee787 !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricDelta"] { color: #79c0ff !important; }
    .stTabs [data-baseweb="tab-list"] { background: #21262d; border-radius: 6px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 4px; }
    .stTabs [aria-selected="true"] { background: #238636 !important; color: #fff !important; }
    hr { border-color: #30363d !important; }
    .stCaption { color: #8b949e !important; }
    [data-testid="stVerticalBlock"] > div { background: transparent; }
</style>
"""
LIGHT_CSS = """
<style>
    .stApp { background-color: #f6f8fa; }
    [data-testid="stHeader"] { background: #ffffff; border-bottom: 1px solid #e1e4e8; }
    [data-testid="stToolbar"] { background: #ffffff !important; }
    [data-testid="stSidebar"] { background: #fafbfc; border-right: 1px solid #e1e4e8; }
    [data-testid="stSidebar"] .stMarkdown { color: #24292e; }
    h1, h2, h3 { color: #0366d6 !important; font-weight: 600; }
    .main-header { color: #0366d6; font-size: 1.75rem; font-weight: 700; letter-spacing: 0.02em; margin-bottom: 0.5rem; }
    .sub-header { color: #586069; font-size: 0.9rem; margin-bottom: 1.5rem; }
    [data-testid="stMetricValue"] { color: #22863a !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #586069 !important; }
    [data-testid="stMetricDelta"] { color: #0366d6 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #ffffff; border: 1px solid #e1e4e8; border-radius: 6px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: #586069; border-radius: 4px; }
    .stTabs [aria-selected="true"] { background: #0366d6 !important; color: #fff !important; }
    hr { border-color: #e1e4e8 !important; }
    .stCaption { color: #586069 !important; }
    [data-testid="stVerticalBlock"] > div { background: transparent; }
</style>
"""


def get_theme_css():
    """Return CSS for current theme so both dark and light moods apply to the whole page."""
    return DARK_CSS if st.session_state.get("theme", "dark") == "dark" else LIGHT_CSS

# =============================================================================
# API configuration
# =============================================================================
def is_production_environment():
    return os.getenv("ENVIRONMENT", "").lower() == "production"


def get_api_base_url():
    url = os.getenv("BACKEND_API_URL", "").strip()
    if not url:
        if is_production_environment():
            logger.warning("BACKEND_API_URL not set in production.")
        url = "http://127.0.0.1:8000"
    return url.rstrip("/")


def check_api_health():
    try:
        r = requests.get(f"{get_api_base_url()}/health", timeout=3)
        return r.status_code == 200, None if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:50]


def check_api_health_with_retry(max_retries=2, delay_seconds=10):
    import time as t
    api_url = get_api_base_url()
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{api_url}/health", timeout=30)
            if r.status_code == 200:
                return True, None, attempt + 1
            if attempt < max_retries - 1:
                t.sleep(delay_seconds)
                continue
            return False, f"HTTP {r.status_code}", attempt + 1
        except Exception as ex:
            if attempt < max_retries - 1:
                t.sleep(delay_seconds)
                continue
            return False, str(ex)[:50], attempt + 1
    return False, "All retries failed", max_retries


# =============================================================================
# Data fetching
# =============================================================================
def fetch_macro_indicators(country_code):
    try:
        r = requests.get(f"{get_api_base_url()}/macro/{country_code}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def fetch_companies():
    try:
        r = requests.get(f"{get_api_base_url()}/companies", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def fetch_forecasts(company):
    try:
        r = requests.get(f"{get_api_base_url()}/forecasts/{company}", timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("count", 0) == 0 or not data.get("data"):
            return None
        return data
    except Exception:
        return None


# =============================================================================
# Fallback data
# =============================================================================
FALLBACK_COMPANIES_CSV = """company,year,revenue,net_income
Apple,2015,233715000000,53394000000
Apple,2016,215639000000,45687000000
Apple,2017,229234000000,48351000000
Apple,2018,265595000000,59531000000
Apple,2019,260174000000,55256000000
Apple,2020,274515000000,57411000000
Apple,2021,365817000000,94680000000
Apple,2022,394328000000,99803000000
Apple,2023,383285000000,96995000000
Apple,2024,390000000000,98000000000
Samsung,2015,177440000000,19100000000
Samsung,2016,173000000000,18000000000
Samsung,2017,211000000000,37000000000
Samsung,2018,221000000000,39000000000
Samsung,2019,206000000000,26000000000
Samsung,2020,200000000000,22000000000
Samsung,2021,244000000000,34000000000
Samsung,2022,234000000000,28000000000
Samsung,2023,220000000000,24000000000
Samsung,2024,225000000000,26000000000
"""
FALLBACK_GDP = {
    "years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "india": [2.7e12, 2.9e12, 2.7e12, 3.1e12, 3.4e12, 3.7e12, 3.9e12],
    "brazil": [1.9e12, 1.8e12, 1.4e12, 1.6e12, 1.9e12, 2.1e12, 2.18e12],
}


# Path to local company financials CSV (relative to this file: dashboard/ -> project root -> data/)
COMPANY_FINANCIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "company_financials.csv")


def _normalize_cols(df):
    if df is None or df.empty:
        return df
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    return df


def _parse_companies_df(df):
    """From a df with company, year, revenue_usd (or revenue), net_income_usd (or net_income), return (apple_df, samsung_df) or (None, None)."""
    if df is None or df.empty:
        return None, None
    df = _normalize_cols(df)
    if "revenue" in df.columns and "revenue_usd" not in df.columns:
        df["revenue_usd"] = pd.to_numeric(df["revenue"], errors="coerce")
    if "net_income" in df.columns and "net_income_usd" not in df.columns:
        df["net_income_usd"] = pd.to_numeric(df["net_income"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    if "company" not in df.columns or "revenue_usd" not in df.columns:
        return None, None
    apple = df[df["company"].astype(str).str.strip().str.lower() == "apple"].dropna(subset=["year", "revenue_usd"]).sort_values("year").copy()
    samsung = df[df["company"].astype(str).str.strip().str.lower() == "samsung"].dropna(subset=["year", "revenue_usd"]).sort_values("year").copy()
    if apple.empty or samsung.empty:
        return None, None
    return apple, samsung


def get_companies_df():
    """Return (apple_df, samsung_df, is_fallback). Columns: company, year, revenue_usd, net_income_usd (if present)."""
    raw = fetch_companies()
    if raw and raw.get("data"):
        df = pd.DataFrame(raw["data"])
        df = _normalize_cols(df)
        req = ["company", "year", "revenue_usd"]
        if not df.empty and all(c in df.columns for c in req):
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df["revenue_usd"] = pd.to_numeric(df["revenue_usd"], errors="coerce")
            if "net_income_usd" in df.columns:
                df["net_income_usd"] = pd.to_numeric(df["net_income_usd"], errors="coerce")
            apple, samsung = _parse_companies_df(df)
            if apple is not None and samsung is not None:
                return apple, samsung, False
    # Fallback 1: load from data/company_financials.csv
    if os.path.isfile(COMPANY_FINANCIALS_PATH):
        try:
            fallback = pd.read_csv(COMPANY_FINANCIALS_PATH)
            apple, samsung = _parse_companies_df(fallback)
            if apple is not None and samsung is not None:
                return apple, samsung, True
        except Exception as e:
            logger.warning("Failed to load %s: %s", COMPANY_FINANCIALS_PATH, e)
    # Fallback 2: embedded CSV
    fallback = pd.read_csv(StringIO(FALLBACK_COMPANIES_CSV.strip()))
    apple, samsung = _parse_companies_df(fallback)
    if apple is not None and samsung is not None:
        return apple, samsung, True
    return pd.DataFrame(), pd.DataFrame(), True


def get_macro_df(indicator="GDP"):
    """Return (ind_df, bra_df, is_fallback) for indicator (GDP or Inflation)."""
    ind_raw = fetch_macro_indicators("IND")
    bra_raw = fetch_macro_indicators("BRA")
    if ind_raw and bra_raw and ind_raw.get("data") and bra_raw.get("data"):
        ind_df = _normalize_cols(pd.DataFrame(ind_raw["data"]))
        bra_df = _normalize_cols(pd.DataFrame(bra_raw["data"]))
        if "indicator" in ind_df.columns and "year" in ind_df.columns and "value" in ind_df.columns:
            ind_f = ind_df[ind_df["indicator"] == indicator].copy()
            bra_f = bra_df[bra_df["indicator"] == indicator].copy()
            if not ind_f.empty and not bra_f.empty:
                return ind_f, bra_f, False
    if indicator == "GDP":
        y = FALLBACK_GDP["years"]
        ind_df = pd.DataFrame({"year": y, "indicator": "GDP", "value": FALLBACK_GDP["india"]})
        bra_df = pd.DataFrame({"year": y, "indicator": "GDP", "value": FALLBACK_GDP["brazil"]})
        return ind_df, bra_df, True
    return None, None, False


def get_forecast_df(company):
    """Return (forecast_df, historical_df, is_estimated). forecast_df: year, forecast_value, model_used."""
    raw = fetch_forecasts(company)
    apple, samsung, _ = get_companies_df()
    hist = apple if company == "Apple" else samsung
    if raw and raw.get("data"):
        df = pd.DataFrame(raw["data"])
        df = _normalize_cols(df)
        if not df.empty and "year" in df.columns and "forecast_value" in df.columns and "model_used" in df.columns:
            return df, hist, False
    # Generate linear forecast
    if hist.empty or "revenue_usd" not in hist.columns:
        return pd.DataFrame(), hist, True
    df = hist.tail(5)
    if len(df) < 2:
        return pd.DataFrame(), hist, True
    X = df["year"].values.reshape(-1, 1)
    y = df["revenue_usd"].values
    model = LinearRegression()
    model.fit(X, y)
    last_year = int(df["year"].max())
    future = np.array([last_year + i for i in range(1, 6)]).reshape(-1, 1)
    pred = np.maximum(model.predict(future), 0)
    forecast_df = pd.DataFrame({
        "year": future.flatten(),
        "forecast_value": pred,
        "model_used": "Linear Regression",
    })
    return forecast_df, hist, True


def filter_by_year_range(df, year_min, year_max, year_col="year"):
    if df is None or df.empty or year_col not in df.columns:
        return df
    df = df.copy()
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    return df[(df[year_col] >= year_min) & (df[year_col] <= year_max)]


def compute_cagr(series_df, year_min, year_max, value_col="revenue_usd", year_col="year"):
    """CAGR (decimal) over period; None if insufficient data."""
    if series_df is None or series_df.empty or value_col not in series_df.columns:
        return None
    df = filter_by_year_range(series_df, year_min, year_max, year_col)
    if df.empty or len(df) < 2:
        return None
    df = df.sort_values(year_col)
    start_val = df[value_col].iloc[0]
    end_val = df[value_col].iloc[-1]
    if start_val <= 0 or end_val <= 0:
        return None
    n = df[year_col].iloc[-1] - df[year_col].iloc[0]
    if n <= 0:
        return None
    return (end_val / start_val) ** (1 / n) - 1


def format_currency(value):
    if value is None or (isinstance(value, float) and (np.isnan(value) or value < 0)):
        return "—"
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    if value >= 1e6:
        return f"${value/1e6:.0f}M"
    return f"${value:,.0f}"


def get_plotly_template():
    """Return Plotly template from session theme (used by all charts)."""
    return "plotly_dark" if st.session_state.get("theme", "dark") == "dark" else "plotly_white"


# Plotly base layout — no height here to avoid duplicate keyword in update_layout()
CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(22,27,34,0.9)",
    "font": {"color": "#c9d1d9", "size": 12},
    "xaxis": {"gridcolor": "#30363d", "zerolinecolor": "#30363d"},
    "yaxis": {"gridcolor": "#30363d", "zerolinecolor": "#30363d"},
    "hovermode": "x unified",
    "margin": {"t": 40, "b": 40, "l": 50, "r": 30},
    "legend": {"bgcolor": "rgba(22,27,34,0.8)", "font": {"color": "#c9d1d9"}},
}


# =============================================================================
# New chart/KPI helpers (append-only; used below existing charts)
# =============================================================================
def _render_analytics_kpis_5(df):
    """Render 5 st.metric cards: Total Apple, Total Samsung, Apple CAGR, Samsung CAGR, Latest YoY %."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        for _ in range(5):
            st.metric("—", "—", help="No data")
        return
    df = df.copy()
    total_apple = df.loc[df["company"].astype(str).str.strip().str.lower() == "apple", "revenue_usd"].sum()
    total_samsung = df.loc[df["company"].astype(str).str.strip().str.lower() == "samsung", "revenue_usd"].sum()
    apple_df = df[df["company"].astype(str).str.strip().str.lower() == "apple"].sort_values("year")
    samsung_df = df[df["company"].astype(str).str.strip().str.lower() == "samsung"].sort_values("year")
    y_min, y_max = df["year"].min(), df["year"].max()
    n_years = max(1, y_max - y_min)
    cagr_apple = (apple_df["revenue_usd"].iloc[-1] / apple_df["revenue_usd"].iloc[0]) ** (1 / n_years) - 1 if len(apple_df) >= 2 and apple_df["revenue_usd"].iloc[0] > 0 else None
    cagr_samsung = (samsung_df["revenue_usd"].iloc[-1] / samsung_df["revenue_usd"].iloc[0]) ** (1 / n_years) - 1 if len(samsung_df) >= 2 and samsung_df["revenue_usd"].iloc[0] > 0 else None
    by_year = df.groupby("year")["revenue_usd"].sum().sort_index()
    yoy_pct = by_year.pct_change().iloc[-1] * 100 if len(by_year) >= 2 else None
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Apple Revenue", format_currency(total_apple) if pd.notna(total_apple) and total_apple != 0 else "—", help="Sum revenue Apple")
    with c2:
        st.metric("Total Samsung Revenue", format_currency(total_samsung) if pd.notna(total_samsung) and total_samsung != 0 else "—", help="Sum revenue Samsung")
    with c3:
        st.metric("Apple CAGR", f"{cagr_apple * 100:.1f}%" if cagr_apple is not None else "—", help="CAGR (last/first)^(1/n)-1")
    with c4:
        st.metric("Samsung CAGR", f"{cagr_samsung * 100:.1f}%" if cagr_samsung is not None else "—", help="CAGR (last/first)^(1/n)-1")
    with c5:
        st.metric("Latest YoY Growth %", f"{yoy_pct:.1f}%" if yoy_pct is not None and pd.notna(yoy_pct) else "—", help="Year-over-year % change")


def create_kpi_cards(df, forecast_next=None):
    """Render 4 st.metric cards: Total revenue (10yr), CAGR, Latest YoY growth, Forecast next year."""
    total_rev = "—"
    cagr_str = "—"
    yoy_str = "—"
    fcast_str = format_currency(forecast_next) if forecast_next is not None and (isinstance(forecast_next, (int, float)) and not np.isnan(forecast_next)) else "—"
    if df is not None and not df.empty and "revenue_usd" in df.columns:
        total_rev = format_currency(df["revenue_usd"].sum())
        by_year = df.groupby("year")["revenue_usd"].sum().sort_index()
        if len(by_year) >= 2:
            n = by_year.index[-1] - by_year.index[0]
            if n > 0 and by_year.iloc[0] > 0:
                cagr_str = f"{(by_year.iloc[-1] / by_year.iloc[0]) ** (1 / n) - 1:.1%}"
            yoy_str = f"{by_year.pct_change().iloc[-1] * 100:.1f}%"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total revenue (10yr)", total_rev, help="Sum revenue in range")
    with c2:
        st.metric("CAGR", cagr_str, help="Compound annual growth rate")
    with c3:
        st.metric("Latest YoY growth", yoy_str, help="Year-over-year %")
    with c4:
        st.metric("Forecast next year", fcast_str, help="First forecast year")


def create_revenue_share_donut(df):
    """Plotly pie with hole=0.6, Apple vs Samsung total revenue share. Title: Revenue Market Share. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share")
    by_company = df.groupby(df["company"].astype(str).str.strip())["revenue_usd"].sum().reset_index()
    by_company.columns = ["company", "revenue"]
    if by_company["revenue"].sum() == 0:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share")
    fig = px.pie(by_company, values="revenue", names="company", hole=0.6, color="company", color_discrete_map={"Apple": "#7ee787", "Samsung": "#79c0ff"})
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share", showlegend=True)
    return fig


def create_s_curve_chart(df):
    """Cumulative revenue growth (S-curve). Sort by year, cumulative sum, Apple + Samsung. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Cumulative Revenue Growth (S-Curve)")
    df = df.sort_values("year")
    fig = go.Figure()
    for name, color in [("Apple", "#7ee787"), ("Samsung", "#79c0ff")]:
        sub = df[df["company"].astype(str).str.strip() == name]
        if sub.empty:
            continue
        sub = sub.sort_values("year")
        cum = sub["revenue_usd"].cumsum()
        fig.add_trace(go.Scatter(x=sub["year"], y=cum, mode="lines", name=name, line=dict(color=color, width=2)))
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Cumulative Revenue Growth (S-Curve)", xaxis_title="Year", yaxis_title="Cumulative Revenue (USD)")
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def create_area_chart(df):
    """Stacked area chart, yearly revenue, Apple + Samsung. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Stacked Revenue Trend")
    df = df.sort_values(["year", "company"])
    fig = go.Figure()
    for name, color in [("Apple", "#7ee787"), ("Samsung", "#79c0ff")]:
        sub = df[df["company"].astype(str).str.strip() == name].sort_values("year")
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(x=sub["year"], y=sub["revenue_usd"], name=name, stackgroup="one", fill="tonexty", line=dict(width=0.5, color=color), fillcolor=color))
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Stacked Revenue Trend", xaxis_title="Year", yaxis_title="Revenue (USD)")
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def create_yoy_growth_bar(df):
    """Year-over-Year growth %, grouped bar, Apple vs Samsung. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Year-over-Year Growth %")
    df = df.sort_values(["company", "year"])
    rows = []
    for name in ["Apple", "Samsung"]:
        sub = df[df["company"].astype(str).str.strip() == name].sort_values("year")
        if len(sub) < 2:
            continue
        sub = sub.copy()
        sub["yoy_pct"] = sub["revenue_usd"].pct_change() * 100
        sub = sub.dropna(subset=["yoy_pct"])
        for _, r in sub.iterrows():
            rows.append({"year": int(r["year"]), "company": name, "yoy_pct": r["yoy_pct"]})
    if not rows:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Year-over-Year Growth %")
    bar_df = pd.DataFrame(rows)
    fig = go.Figure()
    for name, color in [("Apple", "#7ee787"), ("Samsung", "#79c0ff")]:
        sub = bar_df[bar_df["company"] == name]
        if sub.empty:
            continue
        fig.add_trace(go.Bar(x=sub["year"], y=sub["yoy_pct"], name=name, marker_color=color))
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Year-over-Year Growth %", xaxis_title="Year", yaxis_title="YoY %", barmode="group")
    fig.update_yaxes(ticksuffix="%")
    return fig


def create_s_curve(df):
    """Cumulative revenue over years, area-style, separate lines Apple and Samsung, smooth. Returns fig."""
    return create_s_curve_chart(df)


def create_donut_chart(df):
    """Latest year revenue share, Apple vs Samsung, percent labels. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share")
    latest_year = df["year"].max()
    sub = df[df["year"] == latest_year].groupby(df["company"].astype(str).str.strip())["revenue_usd"].sum().reset_index()
    sub.columns = ["company", "revenue"]
    if sub["revenue"].sum() == 0:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share")
    sub["pct"] = (sub["revenue"] / sub["revenue"].sum() * 100).round(1).astype(str) + "%"
    colors = ["#7ee787" if c == "Apple" else "#79c0ff" for c in sub["company"]]
    fig = go.Figure(data=[go.Pie(labels=sub["company"], values=sub["revenue"], hole=0.6, text=sub["pct"], textinfo="text+label", marker=dict(colors=colors))])
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue Market Share (latest year)", showlegend=True)
    return fig


def create_bar_chart(df):
    """Yearly revenue comparison, grouped bars Apple vs Samsung. Returns fig."""
    if df is None or df.empty or "revenue_usd" not in df.columns or "company" not in df.columns:
        return go.Figure().update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Yearly Revenue Comparison")
    fig = go.Figure()
    for name, color in [("Apple", "#7ee787"), ("Samsung", "#79c0ff")]:
        sub = df[df["company"].astype(str).str.strip() == name].sort_values("year")
        if sub.empty:
            continue
        fig.add_trace(go.Bar(x=sub["year"], y=sub["revenue_usd"], name=name, marker_color=color))
    fig.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Yearly Revenue Comparison", xaxis_title="Year", yaxis_title="Revenue (USD)", barmode="group")
    fig.update_yaxes(tickformat="$,.0f")
    return fig


def create_data_table(df):
    """Render full company financials table using st.dataframe."""
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.caption("No data to display.")


# =============================================================================
# Main app
# =============================================================================
def main():
    # ---- Sidebar (theme first so CSS and charts use it this run) ----
    st.sidebar.markdown("### Filters")
    theme_choice = st.sidebar.toggle("🌗 Dark Mode", value=(st.session_state.theme == "dark"), key="theme_toggle")
    st.session_state.theme = "dark" if theme_choice else "light"
    st.markdown(get_theme_css(), unsafe_allow_html=True)

    # ---- Header ----
    st.markdown('<p class="main-header">Smartphone Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Quantitative analytics · Company financials · Macro · Forecasts</p>', unsafe_allow_html=True)

    company = st.sidebar.selectbox("Company", ["Apple", "Samsung"], index=0, key="sb_company")
    year_min, year_max = st.sidebar.slider("Year range", 2014, 2024, (2014, 2024), key="sb_year_range")
    model_choice = st.sidebar.selectbox("Forecast model", ["ARIMA", "Linear Regression"], index=1, key="sb_model")

    # API status (compact)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**API**")
    if "api_ok" not in st.session_state:
        st.session_state.api_ok, st.session_state.api_err = check_api_health()
        if not st.session_state.api_ok and is_production_environment():
            with st.spinner("Waking up backend…"):
                st.session_state.api_ok, st.session_state.api_err, _ = check_api_health_with_retry(2, 10)
    if st.session_state.api_ok:
        st.sidebar.success("Live")
    else:
        st.sidebar.caption(st.session_state.api_err or "Unavailable")
    if st.sidebar.button("Refresh API", key="refresh_api"):
        st.session_state.pop("api_ok", None)
        st.rerun()

    # ---- Data load ----
    apple_df, samsung_df, rev_fallback = get_companies_df()

    # ---- Filters (sidebar): company, year range from df, metric, forecast model ----
    st.sidebar.header("Filters")
    filter_company = st.sidebar.selectbox(
        "Company",
        ["Apple", "Samsung", "Both"],
        index=0,
        key="sb_filter_company",
    )
    _years = pd.concat([apple_df["year"], samsung_df["year"]], ignore_index=True) if not apple_df.empty and not samsung_df.empty else pd.Series([2014, 2024])
    _ymin, _ymax = int(_years.min()), int(_years.max())
    filter_year_min, filter_year_max = st.sidebar.slider(
        "Year range",
        _ymin,
        _ymax,
        (_ymin, _ymax),
        key="sb_filter_year_range",
    )
    filter_metric = st.sidebar.selectbox(
        "Metric",
        ["Revenue", "Net Income"],
        index=0,
        key="sb_filter_metric",
    )
    filter_model = st.sidebar.selectbox(
        "Forecast model",
        ["ARIMA", "Linear Regression"],
        index=1,
        key="sb_filter_model",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Analytics filters**")
    analytics_year_min, analytics_year_max = st.sidebar.slider(
        "Analytics year range",
        _ymin,
        _ymax,
        (_ymin, _ymax),
        key="sb_analytics_year",
    )
    analytics_companies = st.sidebar.multiselect(
        "Companies",
        ["Apple", "Samsung"],
        default=["Apple", "Samsung"],
        key="sb_analytics_companies",
    )
    analytics_forecast_model = st.sidebar.selectbox(
        "Forecast model (analytics)",
        ["ARIMA", "Linear Regression"],
        index=1,
        key="sb_analytics_model",
    )

    company_df = apple_df if company == "Apple" else samsung_df
    company_df = filter_by_year_range(company_df, year_min, year_max)

    try:
        combined = pd.concat([apple_df, samsung_df], ignore_index=True)
    except Exception:
        combined = pd.DataFrame()
    if not combined.empty:
        combined = filter_by_year_range(combined, analytics_year_min, analytics_year_max)
        if analytics_companies:
            combined = combined[combined["company"].astype(str).str.strip().isin(analytics_companies)].copy()
    filtered_df = combined if not combined.empty else pd.DataFrame()

    ind_gdp, bra_gdp, gdp_fallback = get_macro_df("GDP")
    ind_inf, bra_inf, inf_fallback = get_macro_df("Inflation")

    forecast_df, hist_df, forecast_estimated = get_forecast_df(company)
    # Filter forecast by selected model (label may contain "ARIMA" or "Linear")
    if not forecast_df.empty and "model_used" in forecast_df.columns:
        model_col = forecast_df["model_used"].astype(str)
        if "ARIMA" in model_choice.upper():
            forecast_df = forecast_df[model_col.str.upper().str.contains("ARIMA")].copy()
        else:
            forecast_df = forecast_df[model_col.str.upper().str.contains("LINEAR")].copy()

    # KPIs: latest revenue, latest net income, CAGR %, forecast next year
    latest_revenue = None
    latest_net_income = None
    if not company_df.empty:
        row = company_df.loc[company_df["year"].idxmax()]
        latest_revenue = row.get("revenue_usd")
        latest_net_income = row.get("net_income_usd") if "net_income_usd" in company_df.columns else None
    cagr = compute_cagr(company_df, year_min, year_max)
    forecast_next = None
    if not forecast_df.empty and "year" in forecast_df.columns and "forecast_value" in forecast_df.columns:
        first_yr = forecast_df["year"].min()
        forecast_next = forecast_df[forecast_df["year"] == first_yr]["forecast_value"].iloc[0]

    # ---- KPI cards row (5 metrics) ----
    total_records = len(company_df) if not company_df.empty else 0
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Latest revenue", format_currency(latest_revenue) if latest_revenue is not None else "—", help="Most recent year in range")
    with k2:
        st.metric("Latest net income", format_currency(latest_net_income) if latest_net_income is not None else "—", help="Most recent year in range")
    with k3:
        cagr_str = f"{cagr * 100:.1f}%" if cagr is not None else "—"
        st.metric("CAGR %", cagr_str, help=f"CAGR over {year_min}–{year_max}")
    with k4:
        st.metric("Forecast next year", format_currency(forecast_next) if forecast_next is not None else "—", help=f"First forecast year ({model_choice})")
    with k5:
        st.metric("Total records count", str(total_records), help="Filtered financial records")

    st.markdown("---")

    # ---- Tabs ----
    tab_fin, tab_fore, tab_macro, tab_comp = st.tabs(["Financials", "Forecasting", "Macro", "Comparison"])

    # ---------- Financials tab ----------
    with tab_fin:
        st.markdown("#### Financials")
        if company_df.empty:
            st.info("No data in selected year range.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                # Revenue over time
                fig_rev = go.Figure()
                fig_rev.add_trace(go.Scatter(
                    x=company_df["year"], y=company_df["revenue_usd"],
                    mode="lines+markers", name="Revenue",
                    line=dict(color="#7ee787", width=2), marker=dict(size=6),
                ))
                fig_rev.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue over time", xaxis_title="Year", yaxis_title="Revenue (USD)")
                fig_rev.update_yaxes(tickformat="$,.0f")
                st.plotly_chart(fig_rev, use_container_width=True)
            with c2:
                # Net income over time
                if "net_income_usd" in company_df.columns and company_df["net_income_usd"].notna().any():
                    fig_ni = go.Figure()
                    fig_ni.add_trace(go.Scatter(
                        x=company_df["year"], y=company_df["net_income_usd"],
                        mode="lines+markers", name="Net income",
                        line=dict(color="#79c0ff", width=2), marker=dict(size=6),
                    ))
                    fig_ni.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Net income over time", xaxis_title="Year", yaxis_title="Net income (USD)")
                    fig_ni.update_yaxes(tickformat="$,.0f")
                    st.plotly_chart(fig_ni, use_container_width=True)
                else:
                    st.info("Net income not available for this dataset.")
            # YoY growth bar chart
            st.markdown("##### YoY growth (revenue)")
            rev = company_df.sort_values("year")
            if len(rev) >= 2:
                rev = rev.copy()
                rev["yoy_pct"] = rev["revenue_usd"].pct_change() * 100
                rev = rev.dropna(subset=["yoy_pct"])
                fig_yoy = go.Figure()
                fig_yoy.add_trace(go.Bar(
                    x=rev["year"], y=rev["yoy_pct"], name="YoY %",
                    marker_color="#238636", text=rev["yoy_pct"].round(1).astype(str) + "%", textposition="outside",
                ))
                fig_yoy.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Year-over-year revenue growth %", xaxis_title="Year", yaxis_title="YoY %")
                fig_yoy.update_yaxes(ticksuffix="%")
                st.plotly_chart(fig_yoy, use_container_width=True)
            else:
                st.caption("Need at least two years for YoY growth.")

    # ---------- Forecasting tab ----------
    with tab_fore:
        st.markdown("#### Forecasting")
        fig_f = go.Figure()
        if not hist_df.empty and "year" in hist_df.columns and "revenue_usd" in hist_df.columns:
            h = filter_by_year_range(hist_df, year_min, year_max)
            if not h.empty:
                fig_f.add_trace(go.Scatter(
                    x=h["year"], y=h["revenue_usd"], mode="lines+markers", name="Historical",
                    line=dict(color="#7ee787", width=2), marker=dict(size=6),
                ))
        if not forecast_df.empty:
            models = forecast_df["model_used"].unique().tolist() if "model_used" in forecast_df.columns else ["Forecast"]
            colors = ["#f85149", "#79c0ff"]
            for i, m in enumerate(models):
                sub = forecast_df[forecast_df["model_used"] == m] if "model_used" in forecast_df.columns else forecast_df
                if sub.empty:
                    continue
                fig_f.add_trace(go.Scatter(
                    x=sub["year"], y=sub["forecast_value"], mode="lines+markers", name=m,
                    line=dict(color=colors[i % len(colors)], width=2, dash="dash"), marker=dict(size=6),
                ))
        fig_f.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title=f"{company} — Historical + forecast", xaxis_title="Year", yaxis_title="Revenue (USD)")
        fig_f.update_yaxes(tickformat="$,.0f")
        st.plotly_chart(fig_f, use_container_width=True)
        if forecast_estimated:
            st.caption("Forecast is estimated (linear regression) when API forecasts are unavailable.")

    # ---------- Macro tab ----------
    with tab_macro:
        st.markdown("#### Macro")
        col_a, col_b = st.columns(2)
        with col_a:
            if ind_gdp is not None and bra_gdp is not None and not ind_gdp.empty and not bra_gdp.empty:
                fig_gdp = go.Figure()
                fig_gdp.add_trace(go.Scatter(x=ind_gdp["year"], y=ind_gdp["value"], mode="lines+markers", name="India", line=dict(color="#ff7b72", width=2)))
                fig_gdp.add_trace(go.Scatter(x=bra_gdp["year"], y=bra_gdp["value"], mode="lines+markers", name="Brazil", line=dict(color="#79c0ff", width=2)))
                fig_gdp.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="GDP comparison — India vs Brazil", xaxis_title="Year", yaxis_title="GDP (USD)")
                fig_gdp.update_yaxes(tickformat="$,.0f")
                st.plotly_chart(fig_gdp, use_container_width=True)
            else:
                st.info("GDP data not available.")
        with col_b:
            if ind_inf is not None and bra_inf is not None and not ind_inf.empty and not bra_inf.empty:
                fig_inf = go.Figure()
                fig_inf.add_trace(go.Scatter(x=ind_inf["year"], y=ind_inf["value"], mode="lines+markers", name="India", line=dict(color="#ff7b72", width=2)))
                fig_inf.add_trace(go.Scatter(x=bra_inf["year"], y=bra_inf["value"], mode="lines+markers", name="Brazil", line=dict(color="#79c0ff", width=2)))
                fig_inf.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Inflation trend — India vs Brazil", xaxis_title="Year", yaxis_title="Inflation (%)")
                st.plotly_chart(fig_inf, use_container_width=True)
            else:
                st.info("Inflation data not available.")

    # ---------- Comparison tab ----------
    with tab_comp:
        st.markdown("#### Comparison")
        if apple_df.empty or samsung_df.empty:
            st.info("Company data not available.")
        else:
            # Apple vs Samsung revenue same plot
            a = filter_by_year_range(apple_df, year_min, year_max)
            b = filter_by_year_range(samsung_df, year_min, year_max)
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(x=a["year"], y=a["revenue_usd"], mode="lines+markers", name="Apple", line=dict(color="#7ee787", width=2)))
            fig_comp.add_trace(go.Scatter(x=b["year"], y=b["revenue_usd"], mode="lines+markers", name="Samsung", line=dict(color="#79c0ff", width=2)))
            fig_comp.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Apple vs Samsung revenue", xaxis_title="Year", yaxis_title="Revenue (USD)")
            fig_comp.update_yaxes(tickformat="$,.0f")
            st.plotly_chart(fig_comp, use_container_width=True)
            # Market share bar chart (latest year in range)
            st.markdown("##### Market share (revenue, latest year)")
            yr_max = max(a["year"].max(), b["year"].max())
            a_last = a[a["year"] == yr_max]["revenue_usd"].sum()
            b_last = b[b["year"] == yr_max]["revenue_usd"].sum()
            total = a_last + b_last
            if total > 0:
                fig_ms = go.Figure()
                fig_ms.add_trace(go.Bar(x=["Apple", "Samsung"], y=[a_last / 1e9, b_last / 1e9], marker_color=["#7ee787", "#79c0ff"], text=[f"{100*a_last/total:.1f}%", f"{100*b_last/total:.1f}%"], textposition="outside"))
                fig_ms.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Revenue (USD B)", xaxis_title="", yaxis_title="Revenue (USD B)")
                fig_ms.update_yaxes(tickprefix="$", ticksuffix="B")
                st.plotly_chart(fig_ms, use_container_width=True)
            else:
                st.caption("No revenue in selected range for share.")

    # ---- Market Share (donut chart) ----
    st.markdown("---")
    st.markdown("### Market Share")
    a = filter_by_year_range(apple_df, year_min, year_max)
    b = filter_by_year_range(samsung_df, year_min, year_max)
    if not a.empty and not b.empty:
        yr_max = max(a["year"].max(), b["year"].max())
        a_rev = a[a["year"] == yr_max]["revenue_usd"].sum()
        b_rev = b[b["year"] == yr_max]["revenue_usd"].sum()
        total_rev = a_rev + b_rev
        if total_rev > 0:
            share_df = pd.DataFrame({"company": ["Apple", "Samsung"], "revenue": [a_rev, b_rev]})
            fig_donut = px.pie(share_df, values="revenue", names="company", hole=0.5, color="company", color_discrete_map={"Apple": "#7ee787", "Samsung": "#79c0ff"})
            fig_donut.update_layout(**CHART_LAYOUT, template=get_plotly_template(), title="Apple vs Samsung revenue share", showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("No revenue in selected range.")
    else:
        st.caption("Company data not available.")

    # ---- New analytics section (below existing charts) ----
    st.markdown("---")
    st.markdown("### Top analytics (KPI cards)")
    _render_analytics_kpis_5(filtered_df)

    st.markdown("### KPI cards (Total revenue, CAGR, YoY, Forecast)")
    create_kpi_cards(filtered_df, forecast_next)

    st.markdown("---")
    st.markdown("### Revenue Market Share")
    fig_donut_new = create_donut_chart(filtered_df)
    st.plotly_chart(fig_donut_new, use_container_width=True)

    st.markdown("### S-Curve Analysis")
    fig_scurve = create_s_curve(filtered_df)
    st.plotly_chart(fig_scurve, use_container_width=True)

    st.markdown("### Yearly Revenue Comparison")
    fig_bar = create_bar_chart(filtered_df)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### Stacked Revenue Trend")
    fig_area = create_area_chart(filtered_df)
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("### Year-over-Year Growth %")
    fig_yoy_bar = create_yoy_growth_bar(filtered_df)
    st.plotly_chart(fig_yoy_bar, use_container_width=True)

    st.markdown("---")
    st.markdown("### Raw Data Table")
    create_data_table(filtered_df)
    if not filtered_df.empty:
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv_bytes, file_name="smartphone_intelligence_data.csv", mime="text/csv", key="dl_csv")

    st.markdown("---")
    st.caption("Smartphone Intelligence Platform · Data from API when available · Dark theme")


if __name__ == "__main__":
    main()
