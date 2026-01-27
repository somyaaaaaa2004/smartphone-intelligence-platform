"""
Streamlit dashboard for Smartphone Intelligence Platform.
Displays charts by calling FastAPI endpoints.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL - MUST be set via environment variable in production
API_BASE_URL = os.getenv("API_URL", "").strip()

# Detect if running in production (no localhost allowed)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Validate API URL
if not API_BASE_URL:
    if IS_PRODUCTION:
        API_BASE_URL = None  # Will show warning in UI
    else:
        API_BASE_URL = "http://localhost:8000"  # Local development default

# Helper to check if API is configured
def is_api_configured():
    return API_BASE_URL is not None and API_BASE_URL != ""


def fetch_macro_indicators(country_code):
    """
    Fetch macro indicators for a country from Snowflake API.
    Returns live data from Snowflake (no caching for real-time updates).
    """
    if not is_api_configured():
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/macro/{country_code}", timeout=10)
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
    if not is_api_configured():
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/companies", timeout=10)
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
    if not is_api_configured():
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/forecasts/{company}", timeout=10)
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
        
        # Normalize column names to lowercase for case-insensitive access (safe for any column index type)
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
        
        # Normalize column names to lowercase for case-insensitive access (safe for any column index type)
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


def create_kpi_cards():
    """Create KPI cards at the top of the dashboard with loading spinners."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Latest GDP India
    with col1:
        with st.spinner("Loading India GDP..."):
            gdp_ind, yoy_ind = get_latest_gdp("IND")
        if gdp_ind is not None:
            formatted_value = f"${gdp_ind:,.0f}"
            delta_value = f"{yoy_ind:.1f}%" if yoy_ind is not None else None
            st.metric(
                label="🇮🇳 Latest GDP India",
                value=formatted_value,
                delta=delta_value
            )
        else:
            st.metric(label="🇮🇳 Latest GDP India", value="N/A", help="Data unavailable - API may be down")
    
    # Latest GDP Brazil
    with col2:
        with st.spinner("Loading Brazil GDP..."):
            gdp_bra, yoy_bra = get_latest_gdp("BRA")
        if gdp_bra is not None:
            formatted_value = f"${gdp_bra:,.0f}"
            delta_value = f"{yoy_bra:.1f}%" if yoy_bra is not None else None
            st.metric(
                label="🇧🇷 Latest GDP Brazil",
                value=formatted_value,
                delta=delta_value
            )
        else:
            st.metric(label="🇧🇷 Latest GDP Brazil", value="N/A", help="Data unavailable - API may be down")
    
    # Latest Revenue Apple
    with col3:
        with st.spinner("Loading Apple revenue..."):
            rev_apple, yoy_apple = get_latest_revenue("Apple")
        if rev_apple is not None:
            formatted_value = f"${rev_apple:,.0f}"
            delta_value = f"{yoy_apple:.1f}%" if yoy_apple is not None else None
            st.metric(
                label="🍎 Latest Revenue Apple",
                value=formatted_value,
                delta=delta_value
            )
        else:
            st.metric(label="🍎 Latest Revenue Apple", value="N/A", help="Data unavailable - API may be down")
    
    # Latest Revenue Samsung
    with col4:
        with st.spinner("Loading Samsung revenue..."):
            rev_samsung, yoy_samsung = get_latest_revenue("Samsung")
        if rev_samsung is not None:
            formatted_value = f"${rev_samsung:,.0f}"
            delta_value = f"{yoy_samsung:.1f}%" if yoy_samsung is not None else None
            st.metric(
                label="📱 Latest Revenue Samsung",
                value=formatted_value,
                delta=delta_value
            )
        else:
            st.metric(label="📱 Latest Revenue Samsung", value="N/A", help="Data unavailable - API may be down")


def create_gdp_chart(selected_indicator):
    """Create India vs Brazil comparison chart for selected indicator."""
    st.markdown("### 🇮🇳 India vs 🇧🇷 Brazil")
    st.markdown(f"**{selected_indicator} Comparison**")
    
    # Fetch data for both countries with loading spinner
    with st.spinner(f"Loading {selected_indicator} data from Snowflake..."):
        ind_data = fetch_macro_indicators("IND")
        bra_data = fetch_macro_indicators("BRA")
    
    if not ind_data or not bra_data:
        st.warning(f"⚠️ Unable to fetch {selected_indicator} data from API.")
        if not is_api_configured():
            st.error("**API Not Configured:** Set the `API_URL` environment variable to your deployed FastAPI backend URL.")
        else:
            st.info("**Troubleshooting:**\n"
                    "- Ensure the FastAPI backend is deployed and running\n"
                    "- Check that Snowflake connection is configured\n"
                    "- Verify data has been loaded into Snowflake")
        return
    
    try:
        # Filter for selected indicator
        ind_df = pd.DataFrame(ind_data['data'])
        bra_df = pd.DataFrame(bra_data['data'])
        
        # Normalize column names to lowercase (safe for any column index type)
        ind_df.columns = [str(col).lower() for col in ind_df.columns]
        bra_df.columns = [str(col).lower() for col in bra_df.columns]
        
        # Validate required columns exist
        required_columns = ['indicator', 'year', 'value']
        for df_name, df in [('India', ind_df), ('Brazil', bra_df)]:
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                st.error(f"Missing required columns in {df_name} data: {missing}. Available: {list(df.columns)}")
                return
        
        ind_indicator = ind_df[ind_df['indicator'] == selected_indicator].copy()
        bra_indicator = bra_df[bra_df['indicator'] == selected_indicator].copy()
        
        if ind_indicator.empty or bra_indicator.empty:
            st.warning(f"{selected_indicator} data not available for one or both countries.")
            return
    except KeyError as e:
        st.error(f"KeyError in create_gdp_chart: {str(e)}. Please check API response structure.")
        return
    except Exception as e:
        st.error(f"Error processing GDP chart data: {str(e)}")
        return
    
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
    
    fig.update_layout(
        title=f"{selected_indicator} Comparison: India vs Brazil",
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    # Format y-axis based on indicator type
    # Note: Plotly uses update_yaxes (plural), not update_yaxis (singular)
    if selected_indicator in ['GDP', 'GDP per capita']:
        fig.update_yaxes(tickformat='$,.0f')
    elif selected_indicator == 'Inflation':
        fig.update_yaxes(tickformat='.2f')
    else:
        fig.update_yaxes(tickformat=',.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Comparison of {selected_indicator} between India and Brazil over time. Data sourced from World Bank API.")
    
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
    """Create Apple vs Samsung revenue comparison chart."""
    st.markdown("### 🍎 Apple vs 📱 Samsung")
    st.markdown("**Revenue Comparison**")
    
    # Fetch data with loading spinner
    with st.spinner("Loading company revenue data from Snowflake..."):
        companies_data = fetch_companies()
    
    if not companies_data:
        st.warning("⚠️ Unable to fetch company revenue data from API.")
        if not is_api_configured():
            st.error("**API Not Configured:** Set the `API_URL` environment variable to your deployed FastAPI backend URL.")
        else:
            st.info("**Troubleshooting:**\n"
                    "- Ensure the FastAPI backend is deployed and running\n"
                    "- Check that Snowflake connection is configured\n"
                    "- Verify COMPANY_FINANCIALS table has data in Snowflake")
        return
    
    try:
        df = pd.DataFrame(companies_data['data'])
        
        # Normalize column names to lowercase (safe for any column index type)
        df.columns = [str(col).lower() for col in df.columns]
        
        # Validate required columns exist
        required_columns = ['company', 'year', 'revenue_usd']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns in company data: {missing_columns}. Available columns: {list(df.columns)}")
            return
        
        if df.empty:
            st.warning("No company revenue data available.")
            return
        
        # Ensure data types are correct
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
        if 'revenue_usd' in df.columns:
            df['revenue_usd'] = pd.to_numeric(df['revenue_usd'], errors='coerce')
        if 'company' in df.columns:
            df['company'] = df['company'].astype(str)
        
        # Filter for Apple and Samsung
        apple_df = df[df['company'] == 'Apple'].copy()
        samsung_df = df[df['company'] == 'Samsung'].copy()
        
        if apple_df.empty or samsung_df.empty:
            st.warning("Revenue data not available for one or both companies.")
            return
    except KeyError as e:
        st.error(f"KeyError in create_revenue_chart: {str(e)}. Please check API response structure.")
        return
    except Exception as e:
        st.error(f"Error processing revenue chart data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
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
    
    fig.update_layout(
        title="Revenue Comparison: Apple vs Samsung",
        xaxis_title="Year",
        yaxis_title="Revenue (USD)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    # Format y-axis to show values in billions
    # Note: Plotly uses update_yaxes (plural), not update_yaxis (singular)
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Annual revenue comparison between Apple and Samsung. Values in USD.")
    
    # Download button for chart data
    revenue_df = pd.concat([apple_df, samsung_df], ignore_index=True)
    revenue_df = revenue_df[['company', 'year', 'revenue_usd', 'net_income_usd']].sort_values(['company', 'year'])
    csv_data = revenue_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Revenue Data (CSV)",
        data=csv_data,
        file_name="company_revenue_Apple_Samsung.csv",
        mime="text/csv"
    )


def create_forecast_chart(selected_company):
    """Create forecast chart for selected company with model selector."""
    st.markdown(f"**{selected_company} Revenue Forecast - Next 5 Years**")
    
    # Fetch forecast data with loading spinner
    with st.spinner(f"Loading {selected_company} forecasts from Snowflake..."):
        forecasts_data = fetch_forecasts(selected_company)
    
    if not forecasts_data or (isinstance(forecasts_data, dict) and forecasts_data.get('count', 0) == 0):
        st.warning(f"⚠️ No forecasts available for {selected_company}.")
        if not is_api_configured():
            st.error("**API Not Configured:** Set the `API_URL` environment variable to your deployed FastAPI backend URL.")
        else:
            st.info("**To generate forecasts:**\n"
                    "1. Ensure company financial data exists in Snowflake\n"
                    "2. Run the forecasting pipeline: `python -m forecasting.run_forecasts`\n"
                    "3. Migrate forecasts from MySQL to Snowflake if needed")
        return
    
    try:
        df = pd.DataFrame(forecasts_data['data'])
        
        # Normalize column names to lowercase (safe for any column index type)
        df.columns = [str(col).lower() for col in df.columns]
        
        # Validate required columns exist
        required_columns = ['model_used', 'year', 'forecast_value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns in forecast data: {missing_columns}. Available columns: {list(df.columns)}")
            return
        
        if df.empty:
            st.error(f"No forecast data available for {selected_company}.")
            return
        
        # Get available models
        available_models = sorted(df['model_used'].unique().tolist())
    except KeyError as e:
        st.error(f"KeyError in create_forecast_chart: {str(e)}. Please check API response structure.")
        return
    except Exception as e:
        st.error(f"Error processing forecast data: {str(e)}")
        return
    
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
    
    # Filter forecasts by selected model
    if selected_model:
        forecast_df = df[df['model_used'] == selected_model].copy()
    else:
        forecast_df = df.copy()
    
    # Get historical data for context
    companies_data = fetch_companies()
    if companies_data:
        try:
            hist_df = pd.DataFrame(companies_data['data'])
            # Normalize column names to lowercase
            hist_df.columns = [str(col).lower() for col in hist_df.columns]
            
            # Validate required columns exist
            if 'company' in hist_df.columns and 'year' in hist_df.columns and 'revenue_usd' in hist_df.columns:
                company_hist = hist_df[hist_df['company'] == selected_company].copy()
            else:
                st.warning(f"Historical data missing required columns. Available: {list(hist_df.columns)}")
                company_hist = pd.DataFrame()
        except (KeyError, Exception) as e:
            st.warning(f"Error loading historical data: {str(e)}")
            company_hist = pd.DataFrame()
    else:
        company_hist = pd.DataFrame()
    
    # Create plotly chart
    fig = go.Figure()
    
    # Add historical data (solid line)
    if not company_hist.empty:
        fig.add_trace(go.Scatter(
            x=company_hist['year'],
            y=company_hist['revenue_usd'],
            mode='lines+markers',
            name='Historical Revenue',
            line=dict(color='#2c3e50', width=3, dash='solid'),
            marker=dict(size=8, color='#2c3e50')
        ))
    
    # Add forecast data (dashed line)
    if not forecast_df.empty:
        forecast_df_sorted = forecast_df.sort_values('year')
        fig.add_trace(go.Scatter(
            x=forecast_df_sorted['year'],
            y=forecast_df_sorted['forecast_value'],
            mode='lines+markers',
            name=f'Forecast ({selected_model})',
            line=dict(color='#3498db', width=3, dash='dash'),
            marker=dict(size=8, color='#3498db')
        ))
    
    fig.update_layout(
        title=f"{selected_company} Revenue: Historical vs Forecast",
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
    # Note: Plotly uses update_yaxes (plural), not update_yaxis (singular)
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Historical revenue (solid line) and {selected_model} forecast projections (dashed line) for {selected_company}. Forecasts extend 5 years into the future.")
    
    # Download button for forecast data
    download_df = forecast_df[['year', 'forecast_value', 'model_used']].copy()
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
        display_df = forecast_df[['year', 'forecast_value', 'model_used']].copy()
        display_df = display_df.sort_values('year')
        display_df['forecast_value'] = display_df['forecast_value'].apply(lambda x: f"${x:,.0f}")
        display_df.columns = ['Year', 'Forecast Value', 'Model']
        st.dataframe(display_df, use_container_width=True)


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Smartphone Intelligence Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Smartphone Intelligence Platform Dashboard")
    
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
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Status")
    
    # Check if API is configured
    if not is_api_configured():
        st.sidebar.error("❌ API Not Configured")
        st.sidebar.warning("Set `API_URL` environment variable in Render dashboard")
        st.sidebar.caption("Example: `https://your-api.onrender.com`")
    else:
        # Check API health with loading indicator
        with st.sidebar.spinner("Checking API status..."):
            try:
                health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    st.sidebar.success("✅ API Connected")
                    
                    # Show database status
                    if 'databases' in health_data:
                        db_status = health_data['databases']
                        if 'snowflake' in db_status:
                            if db_status['snowflake'] == 'connected':
                                st.sidebar.success("✅ Snowflake Connected")
                            else:
                                st.sidebar.warning(f"⚠️ Snowflake: {db_status.get('snowflake', 'unknown')}")
                                if 'snowflake_error' in db_status:
                                    st.sidebar.caption(f"Error: {db_status['snowflake_error'][:50]}...")
                else:
                    st.sidebar.error("❌ API Error")
                    st.sidebar.caption(f"Status: {health_response.status_code}")
            except requests.exceptions.Timeout:
                st.sidebar.error("❌ API Timeout")
                st.sidebar.caption("API did not respond in time")
            except requests.exceptions.ConnectionError:
                st.sidebar.error("❌ API Unavailable")
                st.sidebar.caption("Cannot connect to API backend")
            except Exception as e:
                st.sidebar.error("❌ API Check Failed")
                st.sidebar.caption(f"Error: {str(e)[:50]}")
        
        st.sidebar.markdown("---")
        st.sidebar.caption(f"**API:** `{API_BASE_URL}`")
    
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
    
    # Footer
    st.markdown("---")
    if is_api_configured():
        st.caption("📊 **Live Data Source:** Smartphone Intelligence Platform API → Snowflake | Data updates in real-time")
    else:
        st.caption("⚠️ **API Not Configured** - Set `API_URL` environment variable to enable live data")


if __name__ == "__main__":
    main()
