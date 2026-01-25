#!/usr/bin/env python3
"""
Quick verification script to test Python 3.13 compatibility and key imports.
Run this before deploying to ensure everything is set up correctly.
"""
import sys
import os

def check_python_version():
    """Check Python version is 3.13+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.13+")
        return False

def check_imports():
    """Check all critical imports work"""
    imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('gunicorn', 'Gunicorn'),
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('plotly', 'Plotly'),
        ('sklearn', 'scikit-learn'),
        ('statsmodels', 'statsmodels'),
        ('snowflake.connector', 'Snowflake Connector'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pymysql', 'PyMySQL'),
        ('requests', 'Requests'),
        ('dotenv', 'python-dotenv'),
    ]
    
    failed = []
    for module_name, display_name in imports:
        try:
            __import__(module_name)
            print(f"✅ {display_name} - Import successful")
        except ImportError as e:
            print(f"❌ {display_name} - Import failed: {e}")
            failed.append(display_name)
    
    return len(failed) == 0

def check_pandas_numpy_compatibility():
    """Check pandas and numpy versions and compatibility"""
    try:
        import pandas as pd
        import numpy as np
        
        pd_version = pd.__version__
        np_version = np.__version__
        
        print(f"✅ Pandas {pd_version} - Installed")
        print(f"✅ NumPy {np_version} - Installed")
        
        # Test basic operations
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        arr = np.array([1, 2, 3], dtype=np.float64)
        
        # Test itertuples (Python 3.13 compatible)
        list(df.itertuples(index=False))
        
        # Test numpy array operations
        result = arr * 2
        assert len(result) == 3
        
        print("✅ Pandas/NumPy operations - Working")
        return True
    except Exception as e:
        print(f"❌ Pandas/NumPy compatibility check failed: {e}")
        return False

def check_environment_variables():
    """Check critical environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'SNOWFLAKE_ACCOUNT',
        'SNOWFLAKE_USER',
        'SNOWFLAKE_PASSWORD',
        'SNOWFLAKE_WAREHOUSE',
        'SNOWFLAKE_DATABASE',
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var, '')
        if not value or value.startswith('your_'):
            missing.append(var)
            print(f"⚠️  {var} - Not set or using placeholder")
        else:
            print(f"✅ {var} - Set (value hidden)")
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} environment variables need to be configured")
        return False
    
    return True

def check_snowflake_connection():
    """Test Snowflake connection (if credentials are set)"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if credentials are set
        account = os.getenv('SNOWFLAKE_ACCOUNT', '')
        if not account or account.startswith('your_'):
            print("⚠️  Snowflake connection - Skipped (credentials not configured)")
            return True
        
        # Try to import and test connection
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from pipeline.db_snowflake import get_snowflake_connection
        
        print("🔄 Testing Snowflake connection...")
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ Snowflake connection - Successful")
            return True
        else:
            print("❌ Snowflake connection - Failed (unexpected result)")
            return False
    except Exception as e:
        print(f"❌ Snowflake connection - Failed: {str(e)[:100]}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("Smartphone Intelligence Platform - Setup Verification")
    print("=" * 70)
    print()
    
    results = []
    
    print("1. Python Version Check")
    print("-" * 70)
    results.append(check_python_version())
    print()
    
    print("2. Package Imports Check")
    print("-" * 70)
    results.append(check_imports())
    print()
    
    print("3. Pandas/NumPy Compatibility Check")
    print("-" * 70)
    results.append(check_pandas_numpy_compatibility())
    print()
    
    print("4. Environment Variables Check")
    print("-" * 70)
    results.append(check_environment_variables())
    print()
    
    print("5. Snowflake Connection Check")
    print("-" * 70)
    results.append(check_snowflake_connection())
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🎉 Setup verification successful! Ready for deployment.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n⚠️  Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
