"""
MySQL to Snowflake data pipeline.
Reads COUNTRIES and MACRO_INDICATORS from MySQL and loads into Snowflake.
"""
import pandas as pd
import traceback
import sys

from pipeline.db_mysql import get_mysql_engine
from pipeline.db_snowflake import get_snowflake_connection


def read_mysql_table(engine, table_name):
    """
    Read data from MySQL table into pandas DataFrame.
    
    Args:
        engine: SQLAlchemy engine for MySQL
        table_name (str): Name of the table to read
    
    Returns:
        pd.DataFrame: DataFrame containing table data
    """
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, engine)
    return df


def truncate_snowflake_table(conn, table_name):
    """
    Safely truncate a Snowflake table. Checks if table exists first.
    
    Args:
        conn: Snowflake connection
        table_name (str): Name of the table to truncate
    
    Raises:
        Exception: If truncation fails
    """
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check if table exists first
        check_query = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
        cursor.execute(check_query)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print(f"  Warning: Table {table_name} does not exist, skipping truncate")
            return
        
        # Truncate the table
        cursor.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")
        print(f"  ✓ Truncated table: {table_name}")
        
    except Exception as e:
        error_msg = f"Failed to truncate Snowflake table '{table_name}': {str(e)}"
        print(f"  ERROR: {error_msg}")
        raise Exception(error_msg) from e
    finally:
        if cursor:
            cursor.close()


def load_dataframe_to_snowflake(conn, df, table_name, batch_size=500):
    """
    Load pandas DataFrame into Snowflake table using INSERT with batch processing.
    Uses %s placeholders (pyformat) as required by snowflake-connector-python.
    
    Args:
        conn: Snowflake connection
        df (pd.DataFrame): DataFrame to load
        table_name (str): Target table name
        batch_size (int): Batch size for inserts (default: 500)
    
    Raises:
        Exception: If data loading fails
    """
    if df.empty:
        print(f"  ⚠ No data to load into {table_name}")
        return
    
    cursor = None
    insert_query = None
    records = None
    
    try:
        cursor = conn.cursor()
        # Get column names (exclude ID if it's auto-increment)
        # For MACRO_INDICATORS, only use specific columns
        if table_name.upper() == 'MACRO_INDICATORS':
            columns = [col for col in df.columns if col.upper() in ['COUNTRY_CODE', 'YEAR', 'INDICATOR', 'VALUE', 'SOURCE']]
        else:
            columns = [col for col in df.columns if col.upper() != 'ID']
        
        if not columns:
            print(f"  No valid columns to insert into {table_name}")
            return
        
        # Build INSERT query with %s placeholders (Snowflake uses pyformat)
        columns_str = ', '.join(columns)
        # Use %s placeholders - Snowflake connector uses pyformat style
        placeholders = ', '.join(['%s'] * len(columns))
        # Use parameterized query string (no f-string formatting to avoid conflicts)
        insert_query = "INSERT INTO {} ({}) VALUES ({})".format(
            table_name,
            columns_str,
            placeholders
        )
        
        # Convert DataFrame to list of tuples with proper type conversion
        def convert_value(val):
            """Convert pandas/numpy types to Python native types."""
            # Handle NaN/None first
            if pd.isna(val):
                return None
            
            # Convert numpy scalar types to Python native types
            try:
                # Try to get Python native value from numpy scalar
                if hasattr(val, 'item'):
                    converted = val.item()
                    # Ensure it's a native Python type
                    if isinstance(converted, (int, float, str, bool, type(None))):
                        return converted
            except (AttributeError, ValueError, OverflowError):
                pass
            
            # Direct type checking and conversion
            type_name = type(val).__name__
            if 'int' in type_name.lower():
                return int(val)
            if 'float' in type_name.lower():
                return float(val) if not pd.isna(val) else None
            if 'bool' in type_name.lower():
                return bool(val)
            
            # Return as-is for strings and other types
            return val
        
        # Convert DataFrame rows to list of tuples
        # Using itertuples() instead of iterrows() for better performance and Python 3.13 compatibility
        records = []
        for row in df.itertuples(index=False):
            record_values = []
            for col in columns:
                # Access column by attribute name (itertuples returns namedtuple)
                val = getattr(row, col, None)
                converted_val = convert_value(val)
                record_values.append(converted_val)
            records.append(tuple(record_values))
        
        # Validate records match placeholder count
        if records and len(records[0]) != len(columns):
            raise ValueError(
                f"Mismatch: {len(records[0])} values per row but {len(columns)} columns. "
                f"Columns: {columns}, First row: {records[0]}"
            )
        
        # Safe logging
        print(f"  Insert query: {insert_query}")
        if records:
            print(f"  Columns ({len(columns)}): {columns}")
            print(f"  First row length: {len(records[0])}, Placeholder count: {len(columns)}")
            print(f"  First row sample: {records[0]}")
        
        # Insert in batches using executemany with error handling per batch
        # Snowflake connector uses pyformat (%s) for executemany
        total_inserted = 0
        failed_batches = []
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            try:
                # Ensure batch is a list of tuples
                if not isinstance(batch, list):
                    batch = list(batch)
                
                # Verify batch structure
                if batch and not isinstance(batch[0], (tuple, list)):
                    raise TypeError(f"Batch items must be tuples/lists, got {type(batch[0])}")
                
                # Execute batch insert
                cursor.executemany(insert_query, batch)
                total_inserted += len(batch)
                print(f"  ✓ Inserted batch {batch_num}/{total_batches} into {table_name}: {total_inserted}/{len(records)} records")
                
            except Exception as batch_error:
                failed_batches.append({
                    'batch_num': batch_num,
                    'size': len(batch),
                    'error': str(batch_error)
                })
                error_msg = (
                    f"Failed to insert batch {batch_num}/{total_batches} into {table_name}: {str(batch_error)}\n"
                    f"  Batch size: {len(batch)}, Total records so far: {total_inserted}"
                )
                print(f"  ERROR: {error_msg}")
                
                # Continue with next batch instead of failing completely
                # This allows partial success
                continue
        
        if failed_batches:
            error_summary = f"Completed with {len(failed_batches)} failed batch(es) out of {total_batches}"
            print(f"  ⚠ {error_summary}")
            for failed in failed_batches:
                print(f"    - Batch {failed['batch_num']}: {failed['error']}")
            
            if total_inserted == 0:
                # If no records were inserted, raise an error
                raise Exception(f"Failed to insert any records into {table_name}. All batches failed.")
            else:
                # Partial success - log warning but don't fail
                print(f"  ⚠ Partial success: {total_inserted}/{len(records)} records inserted")
        else:
            print(f"  ✓ Successfully loaded {total_inserted} records into {table_name}")
            
    except Exception as e:
        error_msg = f"Failed to load data into Snowflake table '{table_name}': {str(e)}"
        print(f"  ERROR: {error_msg}")
        if insert_query:
            print(f"  Query: {insert_query}")
        if records and len(records) > 0:
            print(f"  Sample record (first row): {records[0]}")
        print(f"  Traceback:\n{traceback.format_exc()}")
        raise Exception(error_msg) from e
    finally:
        if cursor:
            cursor.close()


def ensure_snowflake_tables(conn):
    """
    Ensure Snowflake tables exist. Create if they don't exist.
    
    Args:
        conn: Snowflake connection
    
    Raises:
        Exception: If table creation fails
    """
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create COUNTRIES table if it doesn't exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS COUNTRIES (
                    COUNTRY_CODE VARCHAR(10) PRIMARY KEY,
                    COUNTRY_NAME VARCHAR(100)
                )
            """)
            print("  ✓ COUNTRIES table verified/created")
        except Exception as e:
            error_msg = f"Failed to create COUNTRIES table: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Create MACRO_INDICATORS table if it doesn't exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS MACRO_INDICATORS (
                    ID NUMBER AUTOINCREMENT PRIMARY KEY,
                    COUNTRY_CODE VARCHAR(10),
                    YEAR NUMBER,
                    INDICATOR VARCHAR(50),
                    VALUE DOUBLE,
                    SOURCE VARCHAR(100),
                    UNIQUE(COUNTRY_CODE, YEAR, INDICATOR)
                )
            """)
            print("  ✓ MACRO_INDICATORS table verified/created")
        except Exception as e:
            error_msg = f"Failed to create MACRO_INDICATORS table: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
    except Exception as e:
        error_msg = f"Failed to ensure Snowflake tables exist: {str(e)}"
        print(f"  ERROR: {error_msg}")
        raise Exception(error_msg) from e
    finally:
        if cursor:
            cursor.close()


def main():
    """
    Main function to run the pipeline.
    Handles all connections, errors, and cleanup properly.
    """
    print("=" * 70)
    print("MySQL to Snowflake Pipeline")
    print("=" * 70)
    
    mysql_engine = None
    snowflake_conn = None
    
    try:
        # Get MySQL connection
        print("\n[1/5] Connecting to MySQL...")
        try:
            mysql_engine = get_mysql_engine()
            print("  ✓ MySQL connection established")
        except Exception as e:
            error_msg = f"Failed to connect to MySQL: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Get Snowflake connection
        print("\n[2/5] Connecting to Snowflake...")
        try:
            snowflake_conn = get_snowflake_connection()
            print("  ✓ Snowflake connection established")
        except Exception as e:
            error_msg = f"Failed to connect to Snowflake: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Ensure Snowflake tables exist
        print("\n[3/5] Ensuring Snowflake tables exist...")
        try:
            ensure_snowflake_tables(snowflake_conn)
        except Exception as e:
            error_msg = f"Failed to ensure tables exist: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
        # Process COUNTRIES table
        print("\n[4/5] Processing COUNTRIES table...")
        try:
            print("  Reading from MySQL...")
            countries_df = read_mysql_table(mysql_engine, 'countries')
            print(f"  ✓ Read {len(countries_df)} records from MySQL")
            
            if not countries_df.empty:
                # Convert column names to uppercase for Snowflake
                countries_df.columns = [col.upper() for col in countries_df.columns]
                
                print("  Truncating Snowflake table...")
                truncate_snowflake_table(snowflake_conn, 'COUNTRIES')
                
                print("  Loading into Snowflake...")
                load_dataframe_to_snowflake(snowflake_conn, countries_df, 'COUNTRIES')
                print("  ✓ COUNTRIES table processed successfully")
            else:
                print("  ⚠ No data in COUNTRIES table, skipping")
        except Exception as e:
            error_msg = f"Failed to process COUNTRIES table: {str(e)}"
            print(f"  ERROR: {error_msg}")
            # Continue with next table instead of failing completely
            print("  ⚠ Continuing with next table...")
        
        # Process MACRO_INDICATORS table
        print("\n[5/5] Processing MACRO_INDICATORS table...")
        try:
            print("  Reading from MySQL...")
            macro_df = read_mysql_table(mysql_engine, 'macro_indicators')
            print(f"  ✓ Read {len(macro_df)} records from MySQL")
            
            if not macro_df.empty:
                # Convert column names to uppercase for Snowflake
                macro_df.columns = [col.upper() for col in macro_df.columns]
                
                print("  Truncating Snowflake table...")
                truncate_snowflake_table(snowflake_conn, 'MACRO_INDICATORS')
                
                print("  Loading into Snowflake...")
                load_dataframe_to_snowflake(snowflake_conn, macro_df, 'MACRO_INDICATORS')
                print("  ✓ MACRO_INDICATORS table processed successfully")
            else:
                print("  ⚠ No data in MACRO_INDICATORS table, skipping")
        except Exception as e:
            error_msg = f"Failed to process MACRO_INDICATORS table: {str(e)}"
            print(f"  ERROR: {error_msg}")
            raise Exception(error_msg) from e
        
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
        # Cleanup connections
        print("\nCleaning up connections...")
        if snowflake_conn:
            try:
                snowflake_conn.close()
                print("  ✓ Snowflake connection closed")
            except Exception as e:
                print(f"  ⚠ Warning: Error closing Snowflake connection: {str(e)}")
        
        # MySQL engine cleanup (SQLAlchemy handles this automatically, but we can log it)
        if mysql_engine:
            try:
                mysql_engine.dispose()
                print("  ✓ MySQL connection pool disposed")
            except Exception as e:
                print(f"  ⚠ Warning: Error disposing MySQL engine: {str(e)}")
        
        print("  ✓ Cleanup completed")


if __name__ == "__main__":
    main()
