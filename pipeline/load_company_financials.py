"""
Load company financials from CSV into MySQL.
Reads data/company_financials.csv and loads into company_financials table.
"""
import pandas as pd
import os

from pipeline.db_mysql import get_mysql_engine


def load_company_financials():
    """
    Load company financials CSV into MySQL company_financials table.
    """
    # Get the path to the CSV file
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(script_dir, 'data', 'company_financials.csv')
    
    print("=" * 60)
    print("Company Financials Loader")
    print("=" * 60)
    
    # Read CSV file
    print(f"\nReading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Read {len(df)} records from CSV")
    
    if df.empty:
        print("No data to load")
        return
    
    # Clean nulls - remove rows where required fields are null
    initial_count = len(df)
    df = df.dropna(subset=['company', 'year'])
    removed_count = initial_count - len(df)
    
    if removed_count > 0:
        print(f"Removed {removed_count} rows with null company or year")
    
    # Get MySQL engine
    engine = get_mysql_engine()
    
    print("\nInserting data into MySQL...")
    
    insert_query = """
    INSERT INTO company_financials (company, year, revenue_usd, net_income_usd)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        revenue_usd = VALUES(revenue_usd),
        net_income_usd = VALUES(net_income_usd)
    """
    
    # Convert DataFrame to list of tuples
    # Using itertuples() instead of iterrows() for better performance and Python 3.13 compatibility
    records = [
        (
            row.company,
            int(row.year) if pd.notna(row.year) else None,
            float(row.revenue_usd) if pd.notna(row.revenue_usd) else None,
            float(row.net_income_usd) if pd.notna(row.net_income_usd) else None
        )
        for row in df.itertuples(index=False)
    ]
    
    # Execute in batches
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
    
    print(f"\nSuccessfully inserted/updated {total_inserted} records into company_financials table")
    
    # Print counts per company
    print("\n" + "=" * 60)
    print("Record counts per company:")
    print("=" * 60)
    
    company_counts = df['company'].value_counts().sort_index()
    for company, count in company_counts.items():
        print(f"  {company}: {count} records")
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


def main():
    """Main function to run the pipeline."""
    try:
        load_company_financials()
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
