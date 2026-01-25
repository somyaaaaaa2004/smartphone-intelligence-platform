"""
Forecasting module for company revenue.
Reads Apple and Samsung revenue from MySQL, trains models, and saves forecasts.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.db_mysql import get_mysql_engine


def read_company_revenue(engine, company_name):
    """
    Read revenue data for a specific company from MySQL.
    
    Args:
        engine: SQLAlchemy engine
        company_name (str): Company name (e.g., 'Apple', 'Samsung')
    
    Returns:
        pd.DataFrame: DataFrame with columns: year, revenue_usd
    """
    query = f"""
    SELECT year, revenue_usd
    FROM company_financials
    WHERE company = '{company_name}'
    ORDER BY year
    """
    df = pd.read_sql(query, engine)
    return df


def train_linear_regression(years, revenues):
    """
    Train a Linear Regression model.
    
    Args:
        years: pandas Series of years
        revenues: pandas Series of revenue values
    
    Returns:
        sklearn.linear_model.LinearRegression: Trained model
    """
    # Convert to numpy arrays explicitly for Python 3.13 compatibility
    X = np.array(years.values, dtype=np.float64).reshape(-1, 1)
    y = np.array(revenues.values, dtype=np.float64)
    model = LinearRegression()
    model.fit(X, y)
    return model


def train_arima(revenues):
    """
    Train an ARIMA model.
    
    Args:
        revenues: pandas Series or numpy array of revenue values
    
    Returns:
        tuple: (fitted_model, order) where fitted_model is ARIMAResults and order is (p, d, q)
    """
    # Convert to numpy array explicitly for Python 3.13 compatibility
    if isinstance(revenues, pd.Series):
        revenues_array = np.array(revenues.values, dtype=np.float64)
    else:
        revenues_array = np.array(revenues, dtype=np.float64)
    
    # Use auto_arima-like approach: try different orders
    best_aic = np.inf
    best_model = None
    best_order = None
    
    # Try different ARIMA orders
    for p in range(0, 3):
        for d in range(0, 2):
            for q in range(0, 3):
                try:
                    model = ARIMA(revenues_array, order=(p, d, q))
                    fitted_model = model.fit()
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                        best_order = (p, d, q)
                except Exception:
                    continue
    
    # If no model found, use simple ARIMA(1,1,1)
    if best_model is None:
        model = ARIMA(revenues_array, order=(1, 1, 1))
        best_model = model.fit()
        best_order = (1, 1, 1)
    
    return best_model, best_order


def forecast_linear_regression(model, start_year, n_years):
    """
    Generate forecasts using Linear Regression.
    
    Args:
        model: Trained Linear Regression model
        start_year (int): Starting year for forecast
        n_years (int): Number of years to forecast
    
    Returns:
        list: List of (year, forecast_value) tuples
    """
    # Use explicit dtype for Python 3.13 compatibility
    future_years = np.array(range(start_year, start_year + n_years), dtype=np.float64).reshape(-1, 1)
    forecasts = model.predict(future_years)
    # Ensure forecasts are Python native types
    return [(int(year[0]), float(forecast)) for year, forecast in zip(future_years, forecasts)]


def forecast_arima(model, n_years):
    """
    Generate forecasts using ARIMA.
    
    Args:
        model: Fitted ARIMA model
        n_years (int): Number of years to forecast
    
    Returns:
        list: List of forecast values as Python floats
    """
    forecast = model.forecast(steps=n_years)
    # Convert to Python native float types for Python 3.13 compatibility
    return [float(f) for f in forecast]


def save_forecasts(engine, forecasts):
    """
    Save forecast results to MySQL forecasts table.
    
    Args:
        engine: SQLAlchemy engine
        forecasts: List of dictionaries with keys: entity_type, entity_name, year, forecast_value, model_used
    """
    if not forecasts:
        return
    
    insert_query = """
    INSERT INTO forecasts (entity_type, entity_name, year, forecast_value, model_used)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    records = [
        (
            f['entity_type'],
            f['entity_name'],
            f['year'],
            f['forecast_value'],
            f['model_used']
        )
        for f in forecasts
    ]
    
    with engine.begin() as conn:
        raw_conn = conn.connection.driver_connection
        cursor = raw_conn.cursor()
        
        try:
            cursor.executemany(insert_query, records)
        finally:
            cursor.close()


def main():
    """Main function to run forecasts."""
    print("=" * 60)
    print("Company Revenue Forecasting")
    print("=" * 60)
    
    engine = get_mysql_engine()
    companies = ['Apple', 'Samsung']
    models_to_train = ['Linear Regression', 'ARIMA']
    forecast_years = 5
    
    all_forecasts = []
    
    for company in companies:
        print(f"\nProcessing {company}...")
        
        # Read historical data
        df = read_company_revenue(engine, company)
        
        if df.empty or len(df) < 3:
            print(f"  Insufficient data for {company}. Skipping.")
            continue
        
        print(f"  Found {len(df)} years of historical data")
        print(f"  Year range: {df['year'].min()} - {df['year'].max()}")
        
        years = df['year']
        revenues = df['revenue_usd']
        last_year = int(years.max())
        start_forecast_year = last_year + 1
        
        # Train and forecast with Linear Regression
        if 'Linear Regression' in models_to_train:
            print(f"\n  Training Linear Regression model...")
            lr_model = train_linear_regression(years, revenues)
            lr_forecasts = forecast_linear_regression(lr_model, start_forecast_year, forecast_years)
            
            for year, value in lr_forecasts:
                all_forecasts.append({
                    'entity_type': 'company_revenue',
                    'entity_name': company,
                    'year': year,
                    'forecast_value': value,
                    'model_used': 'Linear Regression'
                })
            
            print(f"  Linear Regression forecasts:")
            for year, value in lr_forecasts:
                print(f"    {year}: ${value:,.0f}")
        
        # Train and forecast with ARIMA
        if 'ARIMA' in models_to_train:
            print(f"\n  Training ARIMA model...")
            try:
                arima_model, order = train_arima(revenues)
                arima_values = forecast_arima(arima_model, forecast_years)
                
                print(f"  ARIMA order: {order}")
                print(f"  ARIMA forecasts:")
                for i, value in enumerate(arima_values):
                    year = start_forecast_year + i
                    all_forecasts.append({
                        'entity_type': 'company_revenue',
                        'entity_name': company,
                        'year': year,
                        'forecast_value': value,
                        'model_used': 'ARIMA'
                    })
                    print(f"    {year}: ${value:,.0f}")
            except Exception as e:
                print(f"  Error training ARIMA for {company}: {e}")
    
    # Save all forecasts to MySQL
    if all_forecasts:
        print(f"\nSaving {len(all_forecasts)} forecasts to MySQL...")
        save_forecasts(engine, all_forecasts)
        print(f"Successfully saved forecasts to database")
    else:
        print("\nNo forecasts generated.")
    
    print("\n" + "=" * 60)
    print("Forecasting completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
