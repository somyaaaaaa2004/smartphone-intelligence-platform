"""
Test script to verify Snowflake connection and display connection details.
"""
from pipeline.db_snowflake import get_snowflake_connection


def main():
    """Test Snowflake connection and display information."""
    print("=" * 60)
    print("Snowflake Connection Test")
    print("=" * 60)
    
    try:
        print("\nConnecting to Snowflake...")
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        try:
            # Get account details
            print("\nRunning query: SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_ORGANIZATION_NAME(), CURRENT_ACCOUNT_NAME()")
            cursor.execute("""
                SELECT 
                    CURRENT_ACCOUNT(),
                    CURRENT_REGION(),
                    CURRENT_ORGANIZATION_NAME(),
                    CURRENT_ACCOUNT_NAME()
            """)
            account, region, org_name, account_name = cursor.fetchone()
            
            print("\nResults:")
            print(f"  CURRENT_ACCOUNT():           {account}")
            print(f"  CURRENT_REGION():           {region}")
            print(f"  CURRENT_ORGANIZATION_NAME(): {org_name}")
            print(f"  CURRENT_ACCOUNT_NAME():     {account_name}")
            
            print("\n" + "=" * 60)
            print("Connection test successful!")
            print("=" * 60)
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
