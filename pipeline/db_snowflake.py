"""
Snowflake database connection module using snowflake-connector-python.
Reads database credentials from .env file.
"""
import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def resolve_snowflake_account():
    """
    Resolve and validate Snowflake account identifier from environment.
    Supports multiple account identifier formats:
    - ORG-ACCOUNT (e.g., MOPRGFY-EE19523)
    - ACCOUNT.REGION.CLOUD (e.g., LX83893.ap-southeast-1.aws)
    - ACCOUNT.REGION (e.g., LX83893.ap-southeast-1)
    
    Returns:
        tuple: (account_identifier, account_format) where:
            - account_identifier (str): Valid Snowflake account identifier (normalized)
            - account_format (str): Detected format type
    
    Raises:
        ValueError: If account format is invalid
    """
    account = os.getenv('SNOWFLAKE_ACCOUNT', '').strip()
    
    if not account:
        raise ValueError("SNOWFLAKE_ACCOUNT is not set in .env file")
    
    original_account = account
    
    # Detect and normalize account format
    account_format = None
    normalized_account = account
    
    # Check for ORG-ACCOUNT format (contains dash, no dots)
    if '-' in account and '.' not in account:
        parts = account.split('-')
        if len(parts) == 2 and all(part.strip() for part in parts):
            account_format = "ORG-ACCOUNT"
            # Ensure proper format (uppercase is common but lowercase also works)
            normalized_account = account
    
    # Check for ACCOUNT.REGION.CLOUD format (3 parts separated by dots)
    elif account.count('.') == 2:
        parts = account.split('.')
        if len(parts) == 3 and all(part.strip() for part in parts):
            account_format = "ACCOUNT.REGION.CLOUD"
            normalized_account = account
    
    # Check for ACCOUNT.REGION format (2 parts separated by dot)
    elif account.count('.') == 1:
        parts = account.split('.')
        if len(parts) == 2 and all(part.strip() for part in parts):
            account_format = "ACCOUNT.REGION"
            normalized_account = account
    
    # Validate format was detected
    if account_format is None:
        raise ValueError(
            f"Invalid SNOWFLAKE_ACCOUNT format: '{original_account}'\n"
            "Snowflake account must be in one of these formats:\n"
            "  1. Organization-Account: ORG-ACCOUNT (e.g., MOPRGFY-EE19523)\n"
            "  2. Account.Region.Cloud: ACCOUNT.REGION.CLOUD (e.g., LX83893.ap-southeast-1.aws)\n"
            "  3. Account.Region: ACCOUNT.REGION (e.g., LX83893.ap-southeast-1)\n"
            f"Your value '{original_account}' does not match any supported format."
        )
    
    return normalized_account, account_format

def get_snowflake_connection():
    """
    Create and return a Snowflake connection with proper timeouts and retries.
    
    Returns:
        snowflake.connector.SnowflakeConnection: Snowflake connection instance
    """
    account, account_format = resolve_snowflake_account()
    user = os.getenv('SNOWFLAKE_USER', '')
    password = os.getenv('SNOWFLAKE_PASSWORD', '')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', '')
    database = os.getenv('SNOWFLAKE_DATABASE', '')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
    role = os.getenv('SNOWFLAKE_ROLE', '')  # Optional role parameter
    
    # Print resolved account information clearly before connection
    # Note: Password is NOT printed for security
    print("=" * 70)
    print("Snowflake Connection Configuration:")
    print("=" * 70)
    print(f"  Account Format Detected: {account_format}")
    print(f"  Account Identifier:      {account}")
    print(f"  User:                    {user}")
    print(f"  Warehouse:               {warehouse}")
    print(f"  Database:                {database}")
    print(f"  Schema:                   {schema}")
    if role:
        print(f"  Role:                    {role}")
    print(f"  Password:                {'*' * 8} (hidden)")
    print("=" * 70)
    print(f"Attempting connection using {account_format} format...")
    print("=" * 70)
    
    # Build connection parameters
    conn_params = {
        'account': account,
        'user': user,
        'password': password,
        'warehouse': warehouse,
        'database': database,
        'schema': schema,
        'login_timeout': 60,
        'network_timeout': 60
    }
    
    # Add role if specified
    if role:
        conn_params['role'] = role
    
    try:
        conn = snowflake.connector.connect(**conn_params)
        print("✓ Connection established successfully")
        
        # Verify current role and user
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
            result = cursor.fetchone()
            if result:
                current_user, current_role = result
                print(f"  Current User: {current_user}")
                print(f"  Current Role: {current_role}")
                if role and current_role != role:
                    print(f"  ⚠ Warning: Expected role '{role}' but got '{current_role}'")
        finally:
            cursor.close()
        
        return conn
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your account identifier format matches one of:")
        print("   - ORG-ACCOUNT (e.g., MOPRGFY-EE19523)")
        print("   - ACCOUNT.REGION.CLOUD (e.g., LX83893.ap-southeast-1.aws)")
        print("   - ACCOUNT.REGION (e.g., LX83893.ap-southeast-1)")
        print("2. Check your credentials in .env file")
        print("3. Ensure your Snowflake account is active")
        raise
