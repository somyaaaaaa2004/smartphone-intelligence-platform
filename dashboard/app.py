"""
Streamlit dashboard for Smartphone Intelligence Platform.
Displays charts by calling FastAPI endpoints.
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import logging
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

# Load environment variables
load_dotenv()

# Configure logging - production-safe
# Use INFO level in production, DEBUG only in development
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if os.getenv("ENVIRONMENT", "").lower() == "production":
    log_level = "INFO"  # Force INFO in production
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# API Configuration
# =============================================================================

def is_production_environment():
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "").lower() == "production"


def is_using_default_api_url():
    """Check if using the development default API URL."""
    return not os.getenv("BACKEND_API_URL", "").strip()


def get_api_base_url():
    """
    Dynamically resolve the API base URL.
    
    Priority:
    1. BACKEND_API_URL environment variable (if set)
    2. Default to http://127.0.0.1:8000 for local development only
    
    Returns:
        str: The API base URL (without trailing slash)
    """
    url = os.getenv("BACKEND_API_URL", "").strip()
    if not url:
        # Only use default in non-production environments
        if is_production_environment():
            logger.warning("BACKEND_API_URL not set in production! Using default localhost URL.")
        url = "http://127.0.0.1:8000"
    # Remove trailing slash if present
    return url.rstrip("/")


def check_api_health_with_retry(max_retries=2, delay_seconds=10, initial_timeout=3):
    """
    Ping the /health endpoint with retry logic for Render cold starts.
    Performs retry attempts with delay_seconds between attempts.
    Note: First attempt should be done separately with quick check.
    
    Args:
        max_retries: Maximum number of retry attempts (default 2, for total of 3 attempts)
        delay_seconds: Delay between retries in seconds (default 10)
        initial_timeout: Timeout for retry attempts (default 3, but can be longer for cold starts)
    
    Returns:
        tuple: (is_available: bool, error_message: str or None, retry_count: int)
    """
    import time
    api_url = get_api_base_url()
    
    # Use longer timeout for retry attempts (cold starts can take 30+ seconds)
    retry_timeout = 30
    
    for attempt in range(max_retries):
        try:
            logger.info(f"API health check retry attempt {attempt + 1}/{max_retries}")
            response = requests.get(f"{api_url}/health", timeout=retry_timeout)
            
            if response.status_code == 200:
                logger.info(f"API health check succeeded on retry attempt {attempt + 1}")
                return True, None, attempt + 1
            
            # HTTP errors (like 502) might be cold start - retry
            if attempt < max_retries - 1:
                logger.info(f"Retry attempt {attempt + 1} failed with HTTP {response.status_code}, waiting {delay_seconds}s before next retry...")
                time.sleep(delay_seconds)
                continue
            else:
                logger.warning(f"All retry attempts failed. Last error: HTTP {response.status_code}")
                return False, f"HTTP {response.status_code}", attempt + 1
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                logger.info(f"Retry attempt {attempt + 1} timed out, waiting {delay_seconds}s before next retry...")
                time.sleep(delay_seconds)
                continue
            else:
                logger.warning(f"All retry attempts timed out")
                return False, "Timeout after retries", attempt + 1
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                logger.info(f"Retry attempt {attempt + 1} connection refused, waiting {delay_seconds}s before next retry...")
                time.sleep(delay_seconds)
                continue
            else:
                logger.warning(f"All retry attempts failed with connection refused")
                return False, "Connection refused", attempt + 1
                
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(f"Retry attempt {attempt + 1} error: {str(e)[:50]}, waiting {delay_seconds}s before next retry...")
                time.sleep(delay_seconds)
                continue
            else:
                logger.warning(f"All retry attempts failed with exception: {str(e)[:50]}")
                return False, str(e)[:50], attempt + 1
    
    return False, "All retry attempts failed", max_retries


def check_api_health():
    """
    Ping the /health endpoint to check API availability.
    Uses 3-second timeout to avoid blocking page load.
    For production with retry logic, use check_api_health_with_retry().
    
    Returns:
        tuple: (is_available: bool, error_message: str or None)
    """
    api_url = get_api_base_url()
    try:
        response = requests.get(f"{api_url}/health", timeout=3)
        if response.status_code == 200:
            return True, None
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, str(e)[:50]


def render_api_status_indicator():
    """
    Render a compact API status indicator with retry logic for Render cold starts.
    Non-blocking: uses cached result if available.
    Shows 'API Available' (green), 'Waking up backend service...' (info), or 'API Unavailable' (red).
    Warns if using default URL in production.
    """
    api_url = get_api_base_url()
    using_default = is_using_default_api_url()
    is_prod = is_production_environment()
    
    # Warn if using default URL in production
    if using_default and is_prod:
        st.warning("⚠️ **Configuration Warning:** Using default API URL in production. "
                   "Set `BACKEND_API_URL` environment variable.")
    
    # Use session state to cache health check result (avoid blocking on every rerun)
    cache_key = "api_health_status"
    retry_key = "api_health_retry_state"
    
    # Check if we have a cached result (valid for this session)
    if cache_key not in st.session_state:
        # First load: perform health check with retry logic
        # For production, use retry logic; for local dev, use quick check
        if is_prod:
            # Production: Quick first check, then retry if needed
            # First attempt: quick check (3 seconds)
            is_available, error_msg = check_api_health()
            
            if not is_available:
                # First attempt failed - show "waking up" message and retry
                # This handles Render cold starts (first request can take 30+ seconds)
                st.session_state[retry_key] = {
                    "checking": True,
                    "attempt": 1
                }
                
                # Perform retries with delays (2 more attempts = 3 total)
                # Show spinner with neutral message during retries
                with st.spinner("Waking up backend service…"):
                    is_available, error_msg, retry_count = check_api_health_with_retry(max_retries=2, delay_seconds=10)
                    # retry_count is number of retries performed (0-2), total attempts = retry_count + 1
                    # Add 1 for the initial attempt
                    total_attempts = retry_count + 1
            else:
                # First attempt succeeded - no retries needed
                retry_count = 0
                total_attempts = 1
                st.session_state[retry_key] = {
                    "checking": False,
                    "attempt": 1
                }
            
            st.session_state[cache_key] = {
                "available": is_available,
                "error": error_msg,
                "retry_count": retry_count,
                "total_attempts": total_attempts
            }
            st.session_state[retry_key]["checking"] = False
        else:
            # Local dev: Quick check only (no retries)
            is_available, error_msg = check_api_health()
            st.session_state[cache_key] = {
                "available": is_available,
                "error": error_msg,
                "retry_count": 0,
                "total_attempts": 1
            }
            st.session_state[retry_key] = {
                "checking": False,
                "attempt": 1
            }
    
    # Get cached result
    status = st.session_state[cache_key]
    is_available = status["available"]
    error_msg = status.get("error")
    retry_count = status.get("retry_count", 0)
    total_attempts = status.get("total_attempts", 1)
    retry_state = st.session_state.get(retry_key, {"checking": False, "attempt": 1})
    
    # Store API availability in session state for footer
    st.session_state["api_available"] = is_available
    
    # Render compact status indicator
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if is_available:
            st.success("✅ **API Available**")
        elif retry_state.get("checking", False):
            # Show neutral message during retry (shouldn't persist after rerun, but handle gracefully)
            st.info("⏳ **Waking up backend service…**")
        elif retry_count > 0 and not is_available:
            # Show error only after all retries failed (3 total attempts)
            st.error(f"❌ **API Unavailable** — {error_msg or 'Unknown error'}")
        else:
            # Initial failure (local dev or edge case)
            st.error(f"❌ **API Unavailable** — {error_msg or 'Unknown error'}")
    
    with col2:
        # Refresh button to re-check API status
        if st.button("🔄 Refresh", key="refresh_api_status", help="Re-check API status"):
            # Clear cache and retry
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            if retry_key in st.session_state:
                del st.session_state[retry_key]
            st.rerun()
    
    # Show API URL in caption
    env_indicator = " (default)" if using_default else ""
    if retry_count > 0 and not is_available:
        st.caption(f"API: `{api_url}`{env_indicator} — Attempted {total_attempts} times")
    else:
        st.caption(f"API: `{api_url}`{env_indicator}")


# =============================================================================
# Data Fetching Functions
# =============================================================================

def fetch_macro_indicators(country_code):
    """
    Fetch macro indicators for a country from Snowflake API.
    Returns live data from Snowflake (no caching for real-time updates).
    """
    api_url = get_api_base_url()
    try:
        response = requests.get(f"{api_url}/macro/{country_code}", timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def fetch_companies():
    """
    Fetch company financials from Snowflake API.
    Returns live data from Snowflake (no caching for real-time updates).
    """
    api_url = get_api_base_url()
    try:
        response = requests.get(f"{api_url}/companies", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def fetch_forecasts(company):
    """
    Fetch forecasts for a company from Snowflake API.
    Returns live data from Snowflake (no caching for real-time updates).
    Returns None if no forecasts available or on error.
    """
    api_url = get_api_base_url()
    try:
        response = requests.get(f"{api_url}/forecasts/{company}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Check if data is empty
            if data.get('count', 0) == 0 or not data.get('data'):
                return None
            return data
        else:
            return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


# =============================================================================
# Data Processing Functions
# =============================================================================

def get_latest_gdp(country_code):
    """
    Get latest GDP value and YoY change for a country.
    Returns (value, yoy_change) or (None, None) if data unavailable.
    Does not display errors (handled by caller).
    """
    try:
        data = fetch_macro_indicators(country_code)
        if not data or 'data' not in data:
            return None, None
        
        df = pd.DataFrame(data['data'])
        
        # Normalize column names to lowercase for case-insensitive access
        df.columns = [str(col).lower() for col in df.columns]
        
        # Validate required columns exist
        required_columns = ['indicator', 'year', 'value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, None
        
        if df.empty:
            return None, None
        
        gdp_df = df[df['indicator'] == 'GDP'].copy()
        
        if gdp_df.empty:
            return None, None
        
        # Validate year and value columns have data
        if 'year' not in gdp_df.columns or 'value' not in gdp_df.columns:
            return None, None
        
        # Get latest year
        if gdp_df['year'].isna().all():
            return None, None
        
        latest = gdp_df.loc[gdp_df['year'].idxmax()]
        latest_value = latest['value']
        latest_year = latest['year']
        
        # Validate values are numeric
        if pd.isna(latest_value) or pd.isna(latest_year):
            return None, None
        
        # Get previous year for YoY calculation
        prev_year_data = gdp_df[gdp_df['year'] == latest_year - 1]
        yoy_change = None
        if not prev_year_data.empty:
            prev_value = prev_year_data.iloc[0]['value']
            if prev_value and prev_value != 0 and not pd.isna(prev_value):
                yoy_change = ((latest_value - prev_value) / prev_value) * 100
        
        return latest_value, yoy_change
    except Exception:
        # Silently return None on any error - caller will handle display
        return None, None


def get_latest_revenue(company_name):
    """
    Get latest revenue value and YoY change for a company.
    Returns (value, yoy_change) or (None, None) if data unavailable.
    Does not display errors (handled by caller).
    """
    try:
        data = fetch_companies()
        if not data or 'data' not in data:
            return None, None
        
        df = pd.DataFrame(data['data'])
        
        # Normalize column names to lowercase for case-insensitive access
        df.columns = [str(col).lower() for col in df.columns]
        
        # Validate required columns exist
        required_columns = ['company', 'year', 'revenue_usd']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, None
        
        if df.empty:
            return None, None
        
        company_df = df[df['company'] == company_name].copy()
        
        if company_df.empty:
            return None, None
        
        # Validate year and revenue_usd columns have data
        if 'year' not in company_df.columns or 'revenue_usd' not in company_df.columns:
            return None, None
        
        # Get latest year
        if company_df['year'].isna().all():
            return None, None
        
        latest = company_df.loc[company_df['year'].idxmax()]
        latest_value = latest['revenue_usd']
        latest_year = latest['year']
        
        # Validate values are numeric
        if pd.isna(latest_value) or pd.isna(latest_year):
            return None, None
        
        # Get previous year for YoY calculation
        prev_year_data = company_df[company_df['year'] == latest_year - 1]
        yoy_change = None
        if not prev_year_data.empty:
            prev_value = prev_year_data.iloc[0]['revenue_usd']
            if prev_value and prev_value != 0 and not pd.isna(prev_value):
                yoy_change = ((latest_value - prev_value) / prev_value) * 100
        
        return latest_value, yoy_change
    except Exception:
        # Silently return None on any error - caller will handle display
        return None, None


# =============================================================================
# KPI Data with Fallback
# =============================================================================

# Hardcoded fallback values (latest known data)
# These are used when API is unavailable to ensure KPIs never show N/A
FALLBACK_KPI_DATA = {
    "india_gdp": {
        "value": 3.9e12,  # 3.9 trillion USD
        "growth": 7.5,    # 7.5% growth
        "label": "🇮🇳 Latest GDP India",
        "source": "fallback"
    },
    "brazil_gdp": {
        "value": 2.18e12,  # 2.18 trillion USD
        "growth": -0.2,    # -0.2% growth
        "label": "🇧🇷 Latest GDP Brazil",
        "source": "fallback"
    },
    "apple_revenue": {
        "value": 383e9,    # 383 billion USD
        "growth": None,    # No growth data
        "label": "🍎 Latest Revenue Apple",
        "source": "fallback"
    },
    "samsung_revenue": {
        "value": 305e9,    # 305 billion USD
        "growth": None,    # No growth data
        "label": "📱 Latest Revenue Samsung",
        "source": "fallback"
    }
}

# Fallback GDP time series data (2018-2024)
# Used when API fails or returns empty data for charts
FALLBACK_GDP_TIMESERIES = {
    "years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "india": [2.7e12, 2.9e12, 2.7e12, 3.1e12, 3.4e12, 3.7e12, 3.9e12],   # USD trillions
    "brazil": [1.9e12, 1.8e12, 1.4e12, 1.6e12, 1.9e12, 2.1e12, 2.18e12]  # USD trillions
}

# Fallback revenue time series data (2019-2023)
# Used when API fails or returns empty data for company revenue charts
FALLBACK_REVENUE_TIMESERIES = {
    "years": [2019, 2020, 2021, 2022, 2023],
    "apple": [260e9, 274e9, 365e9, 394e9, 383e9],      # USD billions
    "samsung": [229e9, 236e9, 244e9, 234e9, 305e9]    # USD billions
}


def get_gdp_timeseries_data(selected_indicator: str) -> tuple:
    """
    Get GDP time series data with API-first approach and fallback.
    
    Args:
        selected_indicator: The indicator to fetch (e.g., 'GDP', 'Population')
    
    Returns:
        tuple: (ind_df, bra_df, is_fallback) - DataFrames for India and Brazil, and fallback flag
    """
    # Only GDP has fallback data
    has_fallback = selected_indicator == "GDP"
    
    # Try to fetch from API
    try:
        ind_data = fetch_macro_indicators("IND")
        bra_data = fetch_macro_indicators("BRA")
        
        if ind_data and bra_data and 'data' in ind_data and 'data' in bra_data:
            ind_df = pd.DataFrame(ind_data['data'])
            bra_df = pd.DataFrame(bra_data['data'])
            
            # Normalize column names
            ind_df.columns = [str(col).lower() for col in ind_df.columns]
            bra_df.columns = [str(col).lower() for col in bra_df.columns]
            
            # Check if required columns exist
            required_columns = ['indicator', 'year', 'value']
            ind_has_cols = all(col in ind_df.columns for col in required_columns)
            bra_has_cols = all(col in bra_df.columns for col in required_columns)
            
            if ind_has_cols and bra_has_cols:
                # Filter for selected indicator
                ind_filtered = ind_df[ind_df['indicator'] == selected_indicator].copy()
                bra_filtered = bra_df[bra_df['indicator'] == selected_indicator].copy()
                
                if not ind_filtered.empty and not bra_filtered.empty:
                    logger.info(f"GDP chart: Fetched {selected_indicator} data from API successfully")
                    return ind_filtered, bra_filtered, False
                else:
                    logger.warning(f"GDP chart: {selected_indicator} data empty after filtering")
            else:
                logger.warning(f"GDP chart: Missing required columns in API response")
        else:
            logger.warning("GDP chart: API returned empty or invalid data")
    
    except Exception as e:
        logger.error(f"GDP chart: Exception fetching data - {str(e)}")
    
    # Use fallback for GDP indicator
    if has_fallback:
        logger.info("GDP chart: Using fallback GDP time series data")
        years = FALLBACK_GDP_TIMESERIES["years"]
        
        ind_df = pd.DataFrame({
            "year": years,
            "indicator": ["GDP"] * len(years),
            "value": FALLBACK_GDP_TIMESERIES["india"]
        })
        
        bra_df = pd.DataFrame({
            "year": years,
            "indicator": ["GDP"] * len(years),
            "value": FALLBACK_GDP_TIMESERIES["brazil"]
        })
        
        return ind_df, bra_df, True
    
    # No fallback for other indicators
    return None, None, False


def get_revenue_timeseries_data() -> tuple:
    """
    Get company revenue time series data with API-first approach and fallback.
    
    Returns:
        tuple: (apple_df, samsung_df, is_fallback, reason) - DataFrames, fallback flag, and reason
    """
    # Try to fetch from API
    try:
        companies_data = fetch_companies()
        
        # Check if API call succeeded
        if companies_data is None:
            # API connection failed
            logger.warning("Revenue chart: API connection failed - using fallback")
            reason = "connection_failed"
        elif companies_data and 'data' in companies_data:
            df = pd.DataFrame(companies_data['data'])
            
            # Normalize column names
            df.columns = [str(col).lower() for col in df.columns]
            
            # Check if required columns exist
            required_columns = ['company', 'year', 'revenue_usd']
            has_required_cols = all(col in df.columns for col in required_columns)
            
            if has_required_cols and not df.empty:
                # Ensure correct data types
                df['year'] = pd.to_numeric(df['year'], errors='coerce')
                df['revenue_usd'] = pd.to_numeric(df['revenue_usd'], errors='coerce')
                df['company'] = df['company'].astype(str)
                
                # Filter for Apple and Samsung
                apple_df = df[df['company'] == 'Apple'].copy()
                samsung_df = df[df['company'] == 'Samsung'].copy()
                
                if not apple_df.empty and not samsung_df.empty:
                    logger.info("Revenue chart: Fetched data from API successfully")
                    return apple_df, samsung_df, False, None
                else:
                    logger.warning("Revenue chart: One or both companies missing from API data")
                    reason = "missing_companies"
            else:
                logger.warning(f"Revenue chart: Missing required columns. Has: {list(df.columns) if not df.empty else 'empty'}")
                reason = "invalid_data_format"
        else:
            logger.warning("Revenue chart: API returned empty response")
            reason = "empty_response"
    
    except Exception as e:
        logger.error(f"Revenue chart: Exception fetching data - {str(e)}")
        reason = "exception"
    
    # Use fallback data
    logger.info("Revenue chart: Using fallback revenue time series data")
    years = FALLBACK_REVENUE_TIMESERIES["years"]
    
    apple_df = pd.DataFrame({
        "company": ["Apple"] * len(years),
        "year": years,
        "revenue_usd": FALLBACK_REVENUE_TIMESERIES["apple"],
        "net_income_usd": [None] * len(years)  # No fallback for net income
    })
    
    samsung_df = pd.DataFrame({
        "company": ["Samsung"] * len(years),
        "year": years,
        "revenue_usd": FALLBACK_REVENUE_TIMESERIES["samsung"],
        "net_income_usd": [None] * len(years)  # No fallback for net income
    })
    
    return apple_df, samsung_df, True, reason


def generate_linear_forecast(historical_df: pd.DataFrame, company: str, forecast_years: int = 5) -> pd.DataFrame:
    """
    Generate simple linear forecast using sklearn LinearRegression.
    Uses last 5 years of historical data to predict next 5 years.
    
    Args:
        historical_df: DataFrame with 'year' and 'revenue_usd' columns
        company: Company name for labeling
        forecast_years: Number of years to forecast (default 5)
    
    Returns:
        DataFrame with columns: year, forecast_value, model_used
    """
    try:
        # Ensure we have data
        if historical_df.empty or 'year' not in historical_df.columns or 'revenue_usd' not in historical_df.columns:
            logger.warning(f"Forecast: Cannot generate forecast for {company} - insufficient historical data")
            return pd.DataFrame()
        
        # Clean and prepare data
        df = historical_df.copy()
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['revenue_usd'] = pd.to_numeric(df['revenue_usd'], errors='coerce')
        df = df.dropna(subset=['year', 'revenue_usd'])
        df = df.sort_values('year')
        
        # Use last 5 years for training
        df = df.tail(5)
        
        if len(df) < 2:
            logger.warning(f"Forecast: Not enough data points for {company} - need at least 2")
            return pd.DataFrame()
        
        # Prepare features and target
        X = df['year'].values.reshape(-1, 1)
        y = df['revenue_usd'].values
        
        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecast for next 5 years
        last_year = int(df['year'].max())
        future_years = np.array([last_year + i for i in range(1, forecast_years + 1)]).reshape(-1, 1)
        predictions = model.predict(future_years)
        
        # Ensure predictions are non-negative
        predictions = np.maximum(predictions, 0)
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'year': future_years.flatten(),
            'forecast_value': predictions,
            'model_used': ['Linear Regression (Estimated)'] * forecast_years
        })
        
        logger.info(f"Forecast: Generated linear forecast for {company} ({forecast_years} years)")
        return forecast_df
    
    except Exception as e:
        logger.error(f"Forecast: Error generating forecast for {company} - {str(e)}")
        return pd.DataFrame()


def get_forecast_data(company: str) -> tuple:
    """
    Get forecast data with API-first approach and linear regression fallback.
    
    Args:
        company: Company name (e.g., 'Apple', 'Samsung')
    
    Returns:
        tuple: (forecast_df, historical_df, is_estimated)
               - forecast_df: DataFrame with forecast data
               - historical_df: DataFrame with historical data
               - is_estimated: True if using generated forecast, False if from API
    """
    # Try to fetch forecasts from API
    forecasts_data = fetch_forecasts(company)
    
    # Get historical data (needed for both API and fallback)
    apple_df, samsung_df, hist_is_fallback, _ = get_revenue_timeseries_data()
    historical_df = apple_df if company == "Apple" else samsung_df
    
    # Check if API returned valid forecast data
    if forecasts_data and isinstance(forecasts_data, dict):
        if forecasts_data.get('count', 0) > 0 and forecasts_data.get('data'):
            try:
                df = pd.DataFrame(forecasts_data['data'])
                df.columns = [str(col).lower() for col in df.columns]
                
                required_cols = ['year', 'forecast_value', 'model_used']
                if all(col in df.columns for col in required_cols) and not df.empty:
                    logger.info(f"Forecast: Fetched {company} forecasts from API")
                    return df, historical_df, False
            except Exception as e:
                logger.warning(f"Forecast: Error parsing API forecast data for {company} - {str(e)}")
    
    # Fallback: Generate linear forecast from historical data
    logger.info(f"Forecast: No API forecasts for {company}, generating linear estimate")
    forecast_df = generate_linear_forecast(historical_df, company)
    
    return forecast_df, historical_df, True


def get_kpi_data(kpi_type: str) -> dict:
    """
    Get KPI data with API-first approach and graceful fallback.
    
    Tries to fetch live data from API first. If API fails or returns empty,
    falls back to hardcoded values. Logs all failures for debugging.
    
    GUARANTEED to return a valid dict with 'value', 'growth', 'label', 'source'.
    
    Args:
        kpi_type: One of 'india_gdp', 'brazil_gdp', 'apple_revenue', 'samsung_revenue'
    
    Returns:
        dict with keys: 'value', 'growth', 'label', 'source' ('api' or 'fallback')
    """
    fallback = FALLBACK_KPI_DATA.get(kpi_type, {})
    
    # Defensive: ensure fallback has all required keys
    if not fallback or 'value' not in fallback:
        fallback = {
            "value": 0,
            "growth": None,
            "label": kpi_type.replace("_", " ").title(),
            "source": "fallback"
        }
    
    try:
        # Attempt to fetch from API based on KPI type
        if kpi_type == "india_gdp":
            value, growth = get_latest_gdp("IND")
            if value is not None:
                logger.info(f"KPI '{kpi_type}': Fetched from API successfully")
                return {
                    "value": value,
                    "growth": growth,
                    "label": "🇮🇳 Latest GDP India",
                    "source": "api"
                }
            else:
                logger.warning(f"KPI '{kpi_type}': API returned empty/invalid data, using fallback")
        
        elif kpi_type == "brazil_gdp":
            value, growth = get_latest_gdp("BRA")
            if value is not None:
                logger.info(f"KPI '{kpi_type}': Fetched from API successfully")
                return {
                    "value": value,
                    "growth": growth,
                    "label": "🇧🇷 Latest GDP Brazil",
                    "source": "api"
                }
            else:
                logger.warning(f"KPI '{kpi_type}': API returned empty/invalid data, using fallback")
        
        elif kpi_type == "apple_revenue":
            value, growth = get_latest_revenue("Apple")
            if value is not None:
                logger.info(f"KPI '{kpi_type}': Fetched from API successfully")
                return {
                    "value": value,
                    "growth": growth,
                    "label": "🍎 Latest Revenue Apple",
                    "source": "api"
                }
            else:
                logger.warning(f"KPI '{kpi_type}': API returned empty/invalid data, using fallback")
        
        elif kpi_type == "samsung_revenue":
            value, growth = get_latest_revenue("Samsung")
            if value is not None:
                logger.info(f"KPI '{kpi_type}': Fetched from API successfully")
                return {
                    "value": value,
                    "growth": growth,
                    "label": "📱 Latest Revenue Samsung",
                    "source": "api"
                }
            else:
                logger.warning(f"KPI '{kpi_type}': API returned empty/invalid data, using fallback")
        
        else:
            logger.error(f"KPI '{kpi_type}': Unknown KPI type")
    
    except Exception as e:
        logger.error(f"KPI '{kpi_type}': Exception occurred - {str(e)}")
    
    # Return fallback data
    logger.info(f"KPI '{kpi_type}': Using fallback data")
    return fallback


def format_kpi_value(value: float, is_currency: bool = True) -> str:
    """
    Format KPI value for display.
    NEVER returns N/A - uses fallback display value if needed.
    
    Args:
        value: The numeric value
        is_currency: Whether to add $ prefix
    
    Returns:
        Formatted string (e.g., "$3.9T", "$383B")
    """
    # Defensive: If value is None or invalid, show a placeholder instead of N/A
    if value is None or (isinstance(value, float) and (pd.isna(value) or value < 0)):
        return "$--" if is_currency else "--"
    
    try:
        prefix = "$" if is_currency else ""
        
        if value >= 1e12:
            return f"{prefix}{value/1e12:.1f}T"
        elif value >= 1e9:
            return f"{prefix}{value/1e9:.0f}B"
        elif value >= 1e6:
            return f"{prefix}{value/1e6:.0f}M"
        else:
            return f"{prefix}{value:,.0f}"
    except (TypeError, ValueError):
        return "$--" if is_currency else "--"


# =============================================================================
# UI Components
# =============================================================================

def _render_kpi_card(kpi_type: str, label_override: str = None):
    """
    Helper to render a single KPI card with consistent formatting.
    Guaranteed to render without errors or N/A values.
    """
    kpi = get_kpi_data(kpi_type)
    
    # Defensive: ensure all required fields exist
    value = kpi.get("value", 0)
    growth = kpi.get("growth")
    label = label_override or kpi.get("label", kpi_type.replace("_", " ").title())
    source = kpi.get("source", "fallback")
    
    formatted_value = format_kpi_value(value)
    delta_value = f"{growth:.1f}%" if growth is not None else None
    # Keep wording calm and production-ready
    help_text = (
        "Live data from API"
        if source == "api"
        else "Using latest cached data (most recent values)"
    )
    
    st.metric(
        label=label,
        value=formatted_value,
        delta=delta_value,
        help=help_text
    )
    if source != "api":
        st.caption("📊 Cached data")


def create_kpi_cards():
    """
    Create KPI cards at the top of the dashboard.
    Uses API data when available, falls back to hardcoded values.
    KPIs will NEVER display N/A in production.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    # Latest GDP India
    with col1:
        with st.spinner("Loading..."):
            _render_kpi_card("india_gdp")
    
    # Latest GDP Brazil
    with col2:
        with st.spinner("Loading..."):
            _render_kpi_card("brazil_gdp")
    
    # Latest Revenue Apple
    with col3:
        with st.spinner("Loading..."):
            _render_kpi_card("apple_revenue")
    
    # Latest Revenue Samsung
    with col4:
        with st.spinner("Loading..."):
            _render_kpi_card("samsung_revenue")


def create_gdp_chart(selected_indicator):
    """
    Create India vs Brazil comparison chart for selected indicator.
    Uses API data when available, falls back to hardcoded data for GDP.
    Chart ALWAYS renders - never shows empty state for GDP.
    """
    st.markdown("### 🇮🇳 India vs 🇧🇷 Brazil")
    st.markdown(f"**{selected_indicator} Comparison**")
    
    # Fetch data with fallback support
    with st.spinner(f"Loading {selected_indicator} data..."):
        ind_indicator, bra_indicator, is_fallback = get_gdp_timeseries_data(selected_indicator)
    
    # Check if we have data
    if ind_indicator is None or bra_indicator is None:
        st.warning(f"⚠️ {selected_indicator} data not available.")
        st.info("**Note:** Fallback data is only available for GDP indicator.\n"
                "For other indicators, please ensure the API is running.")
        return
    
    # Show fallback notice if using cached data (calm, informational tone)
    if is_fallback:
        st.info(
            "📊 Showing latest available GDP data "
            "(historical estimates, 2018–2024)."
        )
    
    # Create plotly chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ind_indicator['year'],
        y=ind_indicator['value'],
        mode='lines+markers',
        name='India',
        line=dict(color='#FF9933', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=bra_indicator['year'],
        y=bra_indicator['value'],
        mode='lines+markers',
        name='Brazil',
        line=dict(color='#009739', width=3),
        marker=dict(size=8)
    ))
    
    # Determine y-axis label and format based on indicator
    yaxis_labels = {
        'GDP': 'GDP (USD)',
        'Population': 'Population',
        'Inflation': 'Inflation (%)',
        'GDP per capita': 'GDP per capita (USD)'
    }
    
    yaxis_title = yaxis_labels.get(selected_indicator, selected_indicator)
    
    # Add subtitle if using fallback
    title_suffix = " (Cached Data)" if is_fallback else ""
    
    fig.update_layout(
        title=f"{selected_indicator} Comparison: India vs Brazil{title_suffix}",
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    # Format y-axis based on indicator type
    if selected_indicator in ['GDP', 'GDP per capita']:
        fig.update_yaxes(tickformat='$,.0f')
    elif selected_indicator == 'Inflation':
        fig.update_yaxes(tickformat='.2f')
    else:
        fig.update_yaxes(tickformat=',.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Caption with data source
    if is_fallback:
        st.caption("Data: Cached historical estimates (2018-2024). Connect API for live data.")
    else:
        st.caption(f"Comparison of {selected_indicator} between India and Brazil. Source: World Bank API via Snowflake.")
    
    # Download button for chart data
    combined_df = pd.concat([
        ind_indicator[['year', 'indicator', 'value']].assign(country='India'),
        bra_indicator[['year', 'indicator', 'value']].assign(country='Brazil')
    ], ignore_index=True)
    combined_df = combined_df.sort_values(['country', 'year'])
    csv_data = combined_df.to_csv(index=False)
    st.download_button(
        label=f"📥 Download {selected_indicator} Data (CSV)",
        data=csv_data,
        file_name=f"{selected_indicator.replace(' ', '_')}_IND_BRA.csv",
        mime="text/csv"
    )


def create_revenue_chart():
    """
    Create Apple vs Samsung revenue comparison chart.
    Uses API data when available, falls back to hardcoded data.
    Chart ALWAYS renders - never shows empty state.
    """
    st.markdown("### 🍎 Apple vs 📱 Samsung")
    st.markdown("**Revenue Comparison**")
    
    # Fetch data with fallback support
    with st.spinner("Loading company revenue data..."):
        result = get_revenue_timeseries_data()
        apple_df, samsung_df, is_fallback, reason = result
    
    # Defensive: Ensure we have valid dataframes
    if apple_df is None or samsung_df is None or apple_df.empty or samsung_df.empty:
        st.error("Unable to load revenue data. Please check API connection.")
        return
    
    # Validate required columns exist
    required_cols = ['year', 'revenue_usd']
    if not all(col in apple_df.columns for col in required_cols) or \
       not all(col in samsung_df.columns for col in required_cols):
        st.error("Revenue data missing required columns.")
        return
    
    # Show appropriate message based on fallback reason
    if is_fallback:
        api_url = get_api_base_url()
        if reason == "connection_failed":
            st.info("📊 **Using cached data** — Could not connect to API. Showing historical revenue estimates (2019-2023).")
            st.caption(f"API endpoint: `{api_url}/companies` — Check backend service is running.")
        elif reason == "empty_response":
            st.info("📊 **Using cached data** — API returned no data. Showing historical revenue estimates (2019-2023).")
            st.caption(f"Backend may not have company data loaded. Check Snowflake `COMPANY_FINANCIALS` table.")
        elif reason == "missing_companies":
            st.info("📊 **Using cached data** — Apple/Samsung data not found in API response. Showing historical estimates (2019-2023).")
            st.caption("Verify company names match exactly: 'Apple' and 'Samsung' (case-sensitive).")
        else:
            st.info("📊 **Using cached data** — API data unavailable. Showing historical revenue estimates (2019-2023).")
    
    # Ensure data types are correct
    try:
        apple_df = apple_df.copy()
        samsung_df = samsung_df.copy()
        
        apple_df['year'] = pd.to_numeric(apple_df['year'], errors='coerce')
        apple_df['revenue_usd'] = pd.to_numeric(apple_df['revenue_usd'], errors='coerce')
        samsung_df['year'] = pd.to_numeric(samsung_df['year'], errors='coerce')
        samsung_df['revenue_usd'] = pd.to_numeric(samsung_df['revenue_usd'], errors='coerce')
        
        # Remove any NaN values
        apple_df = apple_df.dropna(subset=['year', 'revenue_usd'])
        samsung_df = samsung_df.dropna(subset=['year', 'revenue_usd'])
        
        # Sort by year
        apple_df = apple_df.sort_values('year')
        samsung_df = samsung_df.sort_values('year')
        
        if apple_df.empty or samsung_df.empty:
            st.error("Revenue data is empty after processing.")
            return
    except Exception as e:
        logger.error(f"Error processing revenue data: {str(e)}")
        st.error(f"Error processing revenue data: {str(e)}")
        return
    
    # Create plotly chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=apple_df['year'],
        y=apple_df['revenue_usd'],
        mode='lines+markers',
        name='Apple',
        line=dict(color='#A8A8A8', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=samsung_df['year'],
        y=samsung_df['revenue_usd'],
        mode='lines+markers',
        name='Samsung',
        line=dict(color='#1428A0', width=3),
        marker=dict(size=8)
    ))
    
    # Add title suffix if using fallback
    title_suffix = " (Cached Data)" if is_fallback else ""
    
    fig.update_layout(
        title=f"Revenue Comparison: Apple vs Samsung{title_suffix}",
        xaxis_title="Year",
        yaxis_title="Revenue (USD)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    # Format y-axis to show values in billions
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Caption with data source
    if is_fallback:
        st.caption("Data: Cached historical estimates (2019-2023). Connect API for live data.")
    else:
        st.caption("Annual revenue comparison between Apple and Samsung. Source: Snowflake via API.")
    
    # Download button for chart data
    revenue_df = pd.concat([apple_df, samsung_df], ignore_index=True)
    # Handle case where net_income_usd might not exist in fallback
    download_cols = ['company', 'year', 'revenue_usd']
    if 'net_income_usd' in revenue_df.columns:
        download_cols.append('net_income_usd')
    revenue_df = revenue_df[download_cols].sort_values(['company', 'year'])
    csv_data = revenue_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Revenue Data (CSV)",
        data=csv_data,
        file_name="company_revenue_Apple_Samsung.csv",
        mime="text/csv"
    )


def create_forecast_chart(selected_company):
    """
    Create forecast chart for selected company.
    Uses API data when available, generates linear forecast as fallback.
    Chart ALWAYS renders - never shows empty state.
    """
    st.markdown(f"**{selected_company} Revenue Forecast - Next 5 Years**")
    
    # Fetch forecast data with fallback support
    with st.spinner(f"Loading {selected_company} forecasts..."):
        forecast_df, historical_df, is_estimated = get_forecast_data(selected_company)
    
    # Check if we have any forecast data
    if forecast_df.empty and historical_df.empty:
        st.error(f"Unable to generate forecast for {selected_company} - no data available.")
        return
    
    # Show estimated badge if using generated forecast
    if is_estimated:
        st.info("📈 **Estimated Forecast** — Using linear regression based on historical revenue data. "
                "Connect API for trained model forecasts.")
    
    # Get available models for selector
    available_models = []
    if not forecast_df.empty and 'model_used' in forecast_df.columns:
        available_models = sorted(forecast_df['model_used'].unique().tolist())
    
    # Model selector dropdown (only show if multiple models exist)
    selected_model = None
    if len(available_models) > 1:
        selected_model = st.selectbox(
            "Select Forecast Model",
            options=available_models,
            index=0,
            key=f"model_selector_{selected_company}"
        )
    elif len(available_models) == 1:
        selected_model = available_models[0]
    else:
        selected_model = "Linear Regression (Estimated)"
    
    # Filter forecasts by selected model if applicable
    if selected_model and not forecast_df.empty:
        filtered_forecast = forecast_df[forecast_df['model_used'] == selected_model].copy()
        if filtered_forecast.empty:
            filtered_forecast = forecast_df.copy()
    else:
        filtered_forecast = forecast_df.copy()
    
    # Create plotly chart
    fig = go.Figure()
    
    # Add historical data (solid line)
    if not historical_df.empty and 'year' in historical_df.columns and 'revenue_usd' in historical_df.columns:
        hist_sorted = historical_df.sort_values('year')
        fig.add_trace(go.Scatter(
            x=hist_sorted['year'],
            y=hist_sorted['revenue_usd'],
            mode='lines+markers',
            name='Historical Revenue',
            line=dict(color='#2c3e50', width=3, dash='solid'),
            marker=dict(size=8, color='#2c3e50')
        ))
    
    # Add forecast data (dashed line)
    if not filtered_forecast.empty:
        forecast_sorted = filtered_forecast.sort_values('year')
        
        # Determine line color based on whether it's estimated
        line_color = '#e74c3c' if is_estimated else '#3498db'
        
        fig.add_trace(go.Scatter(
            x=forecast_sorted['year'],
            y=forecast_sorted['forecast_value'],
            mode='lines+markers',
            name=f'Forecast ({selected_model})',
            line=dict(color=line_color, width=3, dash='dash'),
            marker=dict(size=8, color=line_color)
        ))
    
    # Add title with estimated label if applicable
    title_suffix = " (Estimated)" if is_estimated else ""
    
    fig.update_layout(
        title=f"{selected_company} Revenue: Historical vs Forecast{title_suffix}",
        xaxis_title="Year",
        yaxis_title="Revenue (USD)",
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Format y-axis
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Caption with data source
    if is_estimated:
        st.caption(f"Historical revenue (solid) and estimated linear projection (dashed, red) for {selected_company}. "
                   "Forecast generated using sklearn LinearRegression on last 5 years of data.")
    else:
        st.caption(f"Historical revenue (solid) and {selected_model} forecast (dashed, blue) for {selected_company}. "
                   "Source: Snowflake via API.")
    
    # Download button for forecast data
    if not filtered_forecast.empty:
        download_df = filtered_forecast[['year', 'forecast_value', 'model_used']].copy()
        download_df = download_df.sort_values(['year', 'model_used'])
        download_df.columns = ['Year', 'Forecast Value', 'Model']
        csv_data = download_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {selected_company} Forecast Data (CSV)",
            data=csv_data,
            file_name=f"{selected_company}_forecasts.csv",
            mime="text/csv"
        )
        
        # Display forecast table
        with st.expander("View Forecast Data"):
            display_df = filtered_forecast[['year', 'forecast_value', 'model_used']].copy()
            display_df = display_df.sort_values('year')
            display_df['forecast_value'] = display_df['forecast_value'].apply(lambda x: f"${x:,.0f}")
            display_df.columns = ['Year', 'Forecast Value', 'Model']
            st.dataframe(display_df, use_container_width=True)


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Smartphone Intelligence Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Smartphone Intelligence Platform Dashboard")
    
    # Visible API Status Indicator (at top of page)
    render_api_status_indicator()
    
    st.markdown("---")
    
    # KPI Cards Section
    st.markdown("#### Key Performance Indicators")
    create_kpi_cards()
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # Indicator selector for macro comparison
    selected_indicator = st.sidebar.selectbox(
        "Select Macro Indicator",
        options=["GDP", "Population", "Inflation", "GDP per capita"],
        index=0
    )
    
    # Company selector for forecasts
    selected_company = st.sidebar.selectbox(
        "Select Company for Forecasts",
        options=["Apple", "Samsung"],
        index=0
    )
    
    # Sidebar API info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Configuration")
    api_url = get_api_base_url()
    st.sidebar.code(api_url, language=None)
    
    # Show helpful message based on status
    if is_using_default_api_url() and is_production_environment():
        st.sidebar.error("⚠️ **BACKEND_API_URL not set!**")
        st.sidebar.info("Set `BACKEND_API_URL` environment variable in Render dashboard:\n\n"
                       "1. Go to dashboard service\n"
                       "2. Environment tab\n"
                       "3. Add: `BACKEND_API_URL`\n"
                       "4. Value: Your backend Render URL")
    else:
        st.sidebar.caption("Set `BACKEND_API_URL` env var to change")
    
    # Show connection test button
    if st.sidebar.button("🔍 Test API Connection", key="test_api_connection"):
        is_prod = is_production_environment()
        if is_prod:
            # Production: Use retry logic for cold starts
            with st.sidebar.spinner("Waking up backend service…"):
                # Quick first check
                is_available, error_msg = check_api_health()
                if not is_available:
                    # Retry if first attempt failed
                    is_available, error_msg, retry_count = check_api_health_with_retry(max_retries=2, delay_seconds=10)
        else:
            # Local dev: Quick check
            with st.sidebar.spinner("Testing..."):
                is_available, error_msg = check_api_health()
        
        if is_available:
            st.sidebar.success("✅ API is reachable!")
        else:
            st.sidebar.error(f"❌ Connection failed: {error_msg}")
            st.sidebar.info("**Troubleshooting:**\n"
                           f"- Verify backend URL: `{api_url}`\n"
                           "- Check backend service is 'Live' in Render\n"
                           "- Test backend directly in browser\n"
                           "- Free tier services may take 30+ seconds to wake up")
    
    # Comparison Charts Section
    st.markdown("---")
    st.markdown("#### Comparative Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        create_gdp_chart(selected_indicator)
    
    with col2:
        create_revenue_chart()
    
    # Forecasts Section
    st.markdown("---")
    st.markdown("#### Revenue Forecasts")
    create_forecast_chart(selected_company)
    
    # Footer - dynamically reflect data source
    st.markdown("---")
    api_available = st.session_state.get("api_available", False)
    if api_available:
        st.caption("📊 **Live Data Source:** Smartphone Intelligence Platform API → Snowflake | Data updates in real-time")
    else:
        st.caption("📊 **Data Source:** Using cached/estimated data | Connect API for live updates")


if __name__ == "__main__":
    main()
