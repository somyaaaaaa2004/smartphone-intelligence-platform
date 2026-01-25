"""
World Bank data pipeline to MySQL.
Fetches macroeconomic indicators for India (IND) and Brazil (BRA) and loads into MySQL.
"""
import pandas as pd
import requests
from datetime import datetime

from pipeline.db_mysql import get_mysql_engine

# World Bank API base URL
WORLDBANK_API_BASE = "https://api.worldbank.org/v2"

# Indicator mappings: World Bank indicator code -> display name
INDICATORS = {
    'NY.GDP.MKTP.CD': 'GDP',           # GDP (current US$)
    'SP.POP.TOTL': 'Population',        # Population, total
    'FP.CPI.TOTL.ZG': 'Inflation',      # Inflation, consumer prices (annual %)
    'NY.GDP.PCAP.CD': 'GDP per capita'  # GDP per capita (current US$)
}

# Country codes
COUNTRIES = ['IND', 'BRA']  # India and Brazil


def fetch_worldbank_data(country_code, indicator_code, start_year=2000, end_year=None):
    """
    Fetch data from World Bank API for a specific country and indicator.
    
    Args:
        country_code (str): ISO 3-letter country code (e.g., 'IND', 'BRA')
        indicator_code (str): World Bank indicator code
        start_year (int): Start year for data retrieval
        end_year (int): End year for data retrieval (default: current year)
    
    Returns:
        list: List of dictionaries with year and value
    """
    if end_year is None:
        end_year = datetime.now().year
    
    url = f"{WORLDBANK_API_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {
        'format': 'json',
        'date': f"{start_year}:{end_year}",
        'per_page': 1000
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if len(data) < 2 or not data[1]:
            return []
        
        records = []
        for item in data[1]:
            if item.get('value') is not None:
                records.append({
                    'year': int(item['date']),
                    'value': float(item['value'])
                })
        
        return records
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {country_code}, {indicator_code}: {e}")
        return []


def prepare_dataframe():
    """
    Fetch and prepare World Bank data for all countries and indicators.
    
    Returns:
        pd.DataFrame: DataFrame with columns: country_code, year, indicator, value, source
    """
    all_data = []
    
    print("Fetching World Bank data...")
    for country_code in COUNTRIES:
        print(f"  Processing {country_code}...")
        for indicator_code, indicator_name in INDICATORS.items():
            print(f"    Fetching {indicator_name} ({indicator_code})...")
            records = fetch_worldbank_data(country_code, indicator_code)
            
            for record in records:
                all_data.append({
                    'country_code': country_code,
                    'year': record['year'],
                    'indicator': indicator_name,
                    'value': record['value'],
                    'source': 'World Bank'
                })
    
    df = pd.DataFrame(all_data)
    
    if df.empty:
        print("Warning: No data fetched from World Bank API")
        return df
    
    # Clean nulls - remove rows where value is null
    initial_count = len(df)
    df = df.dropna(subset=['value'])
    removed_count = initial_count - len(df)
    
    if removed_count > 0:
        print(f"Removed {removed_count} rows with null values")
    
    print(f"\nTotal records prepared: {len(df)}")
    print(f"Countries: {df['country_code'].unique().tolist()}")
    print(f"Indicators: {df['indicator'].unique().tolist()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")
    
    return df


def insert_to_mysql(df):
    """
    Insert DataFrame into MySQL macro_indicators table using ON DUPLICATE KEY UPDATE.
    
    Args:
        df (pd.DataFrame): DataFrame with columns: country_code, year, indicator, value, source
    """
    if df.empty:
        print("No data to insert")
        return
    
    engine = get_mysql_engine()
    
    print("\nInserting data into MySQL...")
    
    insert_query = """
    INSERT INTO macro_indicators (country_code, year, indicator, value, source)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        value = VALUES(value),
        source = VALUES(source)
    """
    
    # Convert DataFrame to list of tuples for bulk insert
    # Using itertuples() instead of iterrows() for better performance and Python 3.13 compatibility
    records = [
        (row.country_code, row.year, row.indicator, row.value, row.source)
        for row in df.itertuples(index=False)
    ]
    
    # Execute in batches for better performance
    batch_size = 100
    total_inserted = 0
    
    with engine.begin() as conn:
        # Get the underlying driver connection for executemany
        raw_conn = conn.connection.driver_connection
        cursor = raw_conn.cursor()
        
        try:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                cursor.executemany(insert_query, batch)
                total_inserted += len(batch)
                print(f"  Inserted batch: {total_inserted}/{len(records)} records")
        finally:
            cursor.close()
    
    print(f"\nSuccessfully inserted/updated {total_inserted} records into macro_indicators table")


def main():
    """Main function to run the pipeline."""
    print("=" * 60)
    print("World Bank to MySQL Pipeline")
    print("=" * 60)
    
    # Fetch and prepare data
    df = prepare_dataframe()
    
    if df.empty:
        print("Pipeline completed with no data to insert")
        return
    
    # Insert to MySQL
    insert_to_mysql(df)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
