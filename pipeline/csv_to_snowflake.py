"""
CSV to Snowflake ingestion pipeline.
Loads company_financials.csv into Snowflake COMPANY_FINANCIALS table.
Ensures idempotent loads with no duplicates.
"""
import pandas as pd
import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.db_snowflake import get_snowflake_connection


def ensure_company_financials_table(conn):
    """
    Ensure COMPANY_FINANCIALS table exists in Snowflake.
    Creates table if it doesn't exist with proper schema and unique constraint.
    
    Args:
        conn: Snowflake connection
    
    Raises:
        Exception: If table creation fails
    """
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create COMPANY_FINANCIALS table if it doesn't exist
        # Using UNIQUE constraint on (COMPANY, YEAR) for idempotent loads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS COMPANY_FINANCIALS (
                COMPANY VARCHAR(50),
                YEAR NUMBER,
                REVENUE_USD DOUBLE,
                NET_INCOME_USD DOUBLE,
                UNIQUE(COMPANY, YEAR)
            )
        """)
        print("  ✓ COMPANY_FINANCIALS table verified/created")
        
    except Exception as e:
        error_msg = f"Failed to create COMPANY_FINANCIALS table: {str(e)}"
        print(f"  ERROR: {error_msg}")
        raise Exception(error_msg) from e
    finally:
        if cursor:
            cursor.close()


def get_row_count(conn):
    """
    Get current row count in COMPANY_FINANCIALS table.
    
    Args:
        conn: Snowflake connection
    
    Returns:
        int: Number of rows in the table
    """
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM COMPANY_FINANCIALS")
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"  ⚠ Warning: Could not get row count: {str(e)}")
        return 0
    finally:
        if cursor:
            cursor.close()


def load_company_financials_to_snowflake(conn, df, batch_size=100):
    """
    Load company financials DataFrame into Snowflake using MERGE for idempotent loads.
    Uses MERGE statement to handle duplicates (upsert behavior).
    
    Args:
        conn: Snowflake connection
        df (pd.DataFrame): DataFrame with company financials data
        batch_size (int): Batch size for processing (default: 100)
    
    Returns:
        int: Number of records processed
    """
    if df.empty:
        print("  ⚠ No data to load")
        return 0
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Convert DataFrame column names to uppercase for Snowflake
        df.columns = df.columns.str.upper()
        
        # Ensure required columns exist
        required_columns = ['COMPANY', 'YEAR', 'REVENUE_USD', 'NET_INCOME_USD']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean data - remove rows with null company or year
        initial_count = len(df)
        df = df.dropna(subset=['COMPANY', 'YEAR'])
        cleaned_count = len(df)
        
        if initial_count != cleaned_count:
            print(f"  ⚠ Removed {initial_count - cleaned_count} rows with null COMPANY or YEAR")
        
        if df.empty:
            print("  ⚠ No valid data to load after cleaning")
            return 0
        
        # Convert DataFrame to list of tuples for batch processing
        # Using itertuples() for better performance and Python 3.13 compatibility
        records = []
        for row in df.itertuples(index=False):
            company = row.COMPANY
            year = int(row.YEAR) if pd.notna(row.YEAR) else None
            revenue = float(row.REVENUE_USD) if pd.notna(row.REVENUE_USD) else None
            net_income = float(row.NET_INCOME_USD) if pd.notna(row.NET_INCOME_USD) else None
            
            # Skip rows with missing required fields
            if company is None or year is None:
                continue
            
            records.append((company, year, revenue, net_income))
        
        if not records:
            print("  ⚠ No valid records to insert after processing")
            return 0
        
        # Use MERGE statement for idempotent loads (upsert)
        # This ensures no duplicates even if pipeline runs multiple times
        merge_query = """
        MERGE INTO COMPANY_FINANCIALS AS target
        USING (SELECT %s AS COMPANY, %s AS YEAR, %s AS REVENUE_USD, %s AS NET_INCOME_USD) AS source
        ON target.COMPANY = source.COMPANY AND target.YEAR = source.YEAR
        WHEN MATCHED THEN
            UPDATE SET
                REVENUE_USD = source.REVENUE_USD,
                NET_INCOME_USD = source.NET_INCOME_USD
        WHEN NOT MATCHED THEN
            INSERT (COMPANY, YEAR, REVENUE_USD, NET_INCOME_USD)
            VALUES (source.COMPANY, source.YEAR, source.REVENUE_USD, source.NET_INCOME_USD)
        """
        
        # Process in batches
        total_processed = 0
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                # Execute MERGE for each record in the batch
                for record in batch:
                    cursor.execute(merge_query, record)
                
                total_processed += len(batch)
                print(f"  ✓ Processed batch {batch_num}/{total_batches}: {total_processed}/{len(records)} records")
                
            except Exception as batch_error:
                print(f"  ERROR: Failed to process batch {batch_num}: {str(batch_error)}")
                raise
        
        return total_processed
        
    except Exception as e:
        error_msg = f"Failed to load company financials into Snowflake: {str(e)}"
        print(f"  ERROR: {error_msg}")
        print(f"  Traceback:\n{traceback.format_exc()}")
        raise Exception(error_msg) from e
    finally:
        if cursor:
            cursor.close()


def main():
    """
    Main function to run the CSV to Snowflake ingestion pipeline.
    """
    print("=" * 70)
    print("CSV to Snowflake Ingestion Pipeline")
    print("=" * 70)
    
    snowflake_conn = None
    
    try:
        # Get CSV file path
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(script_dir, 'data', 'company_financials.csv')
        
        # Step 1: Read CSV file
        print("\n[1/5] Reading CSV file...")
        print(f"  Path: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        csv_row_count = len(df)
        print(f"  ✓ Read {csv_row_count} records from CSV")
        
        if df.empty:
            print("  ⚠ CSV file is empty. Nothing to load.")
            return
        
        # Step 2: Connect to Snowflake
        print("\n[2/5] Connecting to Snowflake...")
        try:
            snowflake_conn = get_snowflake_connection()
            print("  ✓ Snowflake connection established")
        except Exception as e:
            error_msg = f"Failed to connect to Snowflake: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Step 3: Ensure table exists
        print("\n[3/5] Ensuring COMPANY_FINANCIALS table exists...")
        try:
            ensure_company_financials_table(snowflake_conn)
        except Exception as e:
            error_msg = f"Failed to ensure table exists: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Step 4: Get row count before load
        print("\n[4/5] Getting row count before load...")
        try:
            row_count_before = get_row_count(snowflake_conn)
            print(f"  ✓ Row count before load: {row_count_before}")
        except Exception as e:
            print(f"  ⚠ Warning: Could not get row count before load: {str(e)}")
            row_count_before = 0
        
        # Step 5: Load data into Snowflake
        print("\n[5/5] Loading data into Snowflake...")
        try:
            records_processed = load_company_financials_to_snowflake(snowflake_conn, df)
            print(f"  ✓ Processed {records_processed} records")
        except Exception as e:
            error_msg = f"Failed to load data: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Get row count after load
        print("\nGetting row count after load...")
        try:
            row_count_after = get_row_count(snowflake_conn)
            print(f"  ✓ Row count after load: {row_count_after}")
            
            # Calculate difference
            rows_added = row_count_after - row_count_before
            print(f"  ✓ Rows added/updated: {rows_added}")
            
            if rows_added != records_processed:
                print(f"  ⚠ Note: Processed {records_processed} records but row count changed by {rows_added}")
                print(f"    This is normal if some records were updates (MERGE behavior)")
        except Exception as e:
            print(f"  ⚠ Warning: Could not get row count after load: {str(e)}")
        
        # Print summary by company
        print("\n" + "=" * 70)
        print("Load Summary by Company:")
        print("=" * 70)
        company_counts = df['company'].value_counts().sort_index() if 'company' in df.columns else df['COMPANY'].value_counts().sort_index()
        for company, count in company_counts.items():
            print(f"  {company}: {count} records")
        
        print("\n" + "=" * 70)
        print("✓ Pipeline completed successfully!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user (Ctrl+C)")
        print("Cleaning up connections...")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ Pipeline failed with error:")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("=" * 70)
        sys.exit(1)
    finally:
        # Cleanup connection
        if snowflake_conn:
            try:
                snowflake_conn.close()
                print("\n✓ Snowflake connection closed")
            except Exception as e:
                print(f"\n⚠ Warning: Error closing Snowflake connection: {str(e)}")


if __name__ == "__main__":
    main()
