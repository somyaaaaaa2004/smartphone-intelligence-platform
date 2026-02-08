"""
Clean, reusable forecasting functions.
Input: pandas Series of historical revenue (index = year for sensible output).
Output: DataFrame with future years + predictions (columns: year, forecast_value).
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA


def _last_year_and_future(series: pd.Series, years: int):
    """Infer last historical year and future year range. Returns (last_year, future_years_array)."""
    if pd.api.types.is_numeric_dtype(series.index) and series.index.min() > 1000:
        last_year = int(series.index.max())
    else:
        last_year = len(series) - 1  # positional
    future_years = np.arange(last_year + 1, last_year + 1 + years, dtype=int)
    return last_year, future_years


def forecast_regression(series: pd.Series, years: int) -> pd.DataFrame:
    """
    Forecast revenue using OLS linear regression (sklearn).

    Parameters
    ----------
    series : pd.Series
        Historical revenue. Index = year (e.g. 2015..2024) for sensible output;
        otherwise integers 0..n-1 are used as time.
    years : int
        Number of future years to forecast.

    Returns
    -------
    pd.DataFrame
        Columns: year, forecast_value. Empty DataFrame if insufficient data.
    """
    if series is None or series.empty or len(series) < 2 or years < 1:
        return pd.DataFrame(columns=["year", "forecast_value"])

    series = series.astype(float)
    if pd.api.types.is_numeric_dtype(series.index) and series.index.min() > 1000:
        hist_years = np.asarray(series.index, dtype=float).reshape(-1, 1)
    else:
        hist_years = np.arange(len(series), dtype=float).reshape(-1, 1)

    X = hist_years
    y = np.asarray(series.values, dtype=float)
    last_year, future_years = _last_year_and_future(series, years)

    model = LinearRegression().fit(X, y)
    pred = model.predict(future_years.reshape(-1, 1))
    pred = np.maximum(pred, 0.0)

    return pd.DataFrame({"year": future_years, "forecast_value": pred})


def forecast_arima(series: pd.Series, years: int) -> pd.DataFrame:
    """
    Forecast revenue using ARIMA (statsmodels).

    Parameters
    ----------
    series : pd.Series
        Historical revenue (ordered by time). Index = year for sensible output years.
    years : int
        Number of future years to forecast.

    Returns
    -------
    pd.DataFrame
        Columns: year, forecast_value. Empty DataFrame if insufficient data or fit failure.
    """
    if series is None or series.empty or len(series) < 3 or years < 1:
        return pd.DataFrame(columns=["year", "forecast_value"])

    y = np.asarray(series.astype(float).values, dtype=float)
    last_year, future_years = _last_year_and_future(series, years)

    orders_to_try = [(2, 1, 2), (1, 1, 1), (1, 0, 1), (1, 1, 0), (0, 1, 1)]
    fit = None
    for order in orders_to_try:
        try:
            model = ARIMA(y, order=order)
            fit = model.fit()
            break
        except Exception:
            continue

    if fit is None:
        return pd.DataFrame(columns=["year", "forecast_value"])

    forecast = fit.forecast(steps=years)
    forecast = np.maximum(np.asarray(forecast, dtype=float), 0.0)

    return pd.DataFrame({"year": future_years, "forecast_value": forecast})
