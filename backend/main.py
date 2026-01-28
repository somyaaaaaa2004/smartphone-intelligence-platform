"""
FastAPI application for smartphone intelligence platform.
Provides REST API endpoints for accessing Snowflake data.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sys
import os
from contextlib import contextmanager
from threading import Lock
from queue import Queue, Empty
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.db_snowflake import get_snowflake_connection

# ============================================================================
# Snowflake Connection Pool
# ============================================================================

class SnowflakeConnectionPool:
    """
    Simple connection pool for Snowflake connections.
    Manages a pool of connections to reduce connection overhead.
    """
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self._pool = Queue(maxsize=max_connections)
        self._lock = Lock()
        self._created = 0
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool. Creates new connection if pool is empty.
        Returns connection to pool when done.
        
        Yields:
            snowflake.connector.SnowflakeConnection: Snowflake connection
        """
        conn = None
        try:
            # Try to get connection from pool
            try:
                conn = self._pool.get_nowait()
            except Empty:
                # Pool is empty, create new connection
                with self._lock:
                    if self._created < self.max_connections:
                        conn = get_snowflake_connection()
                        self._created += 1
                    else:
                        # Wait for a connection to become available
                        conn = self._pool.get(timeout=30)
            
            yield conn
        except Exception as e:
            # If connection is bad, close it and don't return to pool
            if conn:
                try:
                    conn.close()
                except:
                    pass
                with self._lock:
                    self._created -= 1
            raise
        finally:
            # Return connection to pool if it's still valid
            if conn:
                try:
                    # Test if connection is still alive
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    # Connection is good, return to pool
                    try:
                        self._pool.put_nowait(conn)
                    except:
                        # Pool is full, close connection
                        conn.close()
                        with self._lock:
                            self._created -= 1
                except:
                    # Connection is dead, don't return to pool
                    try:
                        conn.close()
                    except:
                        pass
                    with self._lock:
                        self._created -= 1
    
    def close_all(self):
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except:
                pass
        self._created = 0


# ============================================================================
# Helper Functions
# ============================================================================

def convert_snowflake_row_to_dict(row, columns):
    """
    Convert a Snowflake row to a dictionary with lowercase keys.
    Handles type conversion for Python 3.13 compatibility.
    
    Args:
        row: Tuple of row values from Snowflake
        columns: List of column names from cursor.description
    
    Returns:
        dict: Dictionary with lowercase keys and Python native types
    """
    record = dict(zip(columns, row))
    # Convert to lowercase keys for consistency
    record = {k.lower(): v for k, v in record.items()}
    # Convert None/NaN values and numpy types to Python native types
    for key, value in record.items():
        if value is None:
            record[key] = None
        elif hasattr(value, 'item'):
            try:
                record[key] = value.item()
            except:
                record[key] = value
    return record


# ============================================================================
# Environment Variable Validation
# ============================================================================

def validate_environment_variables():
    """
    Validate that all required environment variables are set.
    Raises ValueError with clear error message if any are missing.
    """
    required_vars = {
        'Snowflake': [
            'SNOWFLAKE_ACCOUNT',
            'SNOWFLAKE_USER',
            'SNOWFLAKE_PASSWORD',
            'SNOWFLAKE_WAREHOUSE',
            'SNOWFLAKE_DATABASE',
            'SNOWFLAKE_SCHEMA'
        ]
    }
    
    missing_vars = []
    
    # Check Snowflake variables
    for var in required_vars['Snowflake']:
        value = os.getenv(var, '').strip()
        if not value:
            missing_vars.append(f"  - {var} (Snowflake)")
    
    if missing_vars:
        error_msg = (
            "\n" + "=" * 70 + "\n"
            "ERROR: Missing required environment variables\n"
            "=" * 70 + "\n"
            "The following environment variables are not set:\n"
            + "\n".join(missing_vars) + "\n\n"
            "Please ensure you have:\n"
            "  1. Created a .env file in the project root\n"
            "  2. Copied .env.example to .env (if it exists)\n"
            "  3. Filled in all required values\n\n"
            "Example: Copy .env.example to .env and update with your credentials\n"
            "=" * 70 + "\n"
        )
        raise ValueError(error_msg)
    
    # Validate that variables are not using placeholder values
    placeholder_values = {
        'SNOWFLAKE_ACCOUNT': ['your_snowflake_account_here', ''],
        'SNOWFLAKE_USER': ['your_snowflake_username', ''],
        'SNOWFLAKE_PASSWORD': ['your_snowflake_password_here', ''],
        'SNOWFLAKE_WAREHOUSE': ['your_warehouse_name', ''],
        'SNOWFLAKE_DATABASE': ['your_database_name', '']
    }
    
    invalid_vars = []
    
    for var_name, placeholders in placeholder_values.items():
        value = os.getenv(var_name, '').strip()
        if value in placeholders:
            invalid_vars.append(f"  - {var_name} (still using placeholder value)")
    
    if invalid_vars:
        error_msg = (
            "\n" + "=" * 70 + "\n"
            "ERROR: Snowflake environment variables not configured\n"
            "=" * 70 + "\n"
            "The following variables are using placeholder values:\n"
            + "\n".join(invalid_vars) + "\n\n"
            "Please update your .env file with actual Snowflake configuration values.\n"
            "Copy .env.example to .env and fill in your Snowflake credentials.\n"
            "=" * 70 + "\n"
        )
        raise ValueError(error_msg)


# Configure logging for production
import logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if os.getenv("ENVIRONMENT", "").lower() == "production":
    log_level = "INFO"  # Force INFO in production
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate environment variables on startup
try:
    validate_environment_variables()
    logger.info("Environment variables validated successfully")
except ValueError as e:
    logger.error(str(e))
    raise

app = FastAPI(title="Smartphone Intelligence Platform API", version="1.0.0")

# Initialize Snowflake connection pool
try:
    snowflake_pool = SnowflakeConnectionPool(max_connections=5)
    logger.info("Snowflake connection pool initialized")
except Exception as e:
    logger.error(f"Error initializing Snowflake connection pool: {str(e)}")
    raise


@app.get("/")
async def root():
    """
    Root endpoint - Simple service status and documentation link.
    """
    return {
        "service": "Smartphone Intelligence Platform API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for production monitoring.
    Returns API status, database connection status, and version info.
    Suitable for Kubernetes liveness/readiness probes and load balancer health checks.
    """
    import time
    
    health_status = {
        "status": "healthy",
        "api": "running",
        "version": "1.0.0",
        "timestamp": time.time(),
        "databases": {}
    }
    
    # Check Snowflake connection with timeout
    try:
        with snowflake_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            # Verify we got expected result
            if result and result[0] == 1:
                health_status["databases"]["snowflake"] = "connected"
            else:
                health_status["databases"]["snowflake"] = "unhealthy"
                health_status["status"] = "degraded"
    except Exception as e:
        # Don't expose full error details in production (security)
        error_msg = str(e)
        # Sanitize error message to avoid exposing sensitive info
        if "password" in error_msg.lower() or "credential" in error_msg.lower():
            error_msg = "Connection authentication failed"
        elif "timeout" in error_msg.lower():
            error_msg = "Connection timeout"
        else:
            # Only show first part of error, not full traceback
            error_msg = error_msg.split("\n")[0][:100]
        
        health_status["databases"]["snowflake"] = "disconnected"
        health_status["status"] = "degraded"
        health_status["databases"]["snowflake_error"] = error_msg
    
    # Return appropriate HTTP status code
    if health_status["status"] == "degraded":
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status


@app.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is running (even if databases are down).
    """
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.
    Returns 200 only if the application is ready to serve traffic (databases connected).
    """
    try:
        with snowflake_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})


@app.get("/macro/{country_code}")
async def get_macro_indicators(country_code: str):
    """
    Get macro indicators for a specific country from Snowflake.
    Source of truth: Snowflake MACRO_INDICATORS table.
    
    Args:
        country_code: ISO country code (e.g., 'IND', 'BRA')
    
    Returns:
        JSON response with country_code, count, and data array
    """
    try:
        with snowflake_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Parameterized query to prevent SQL injection
            query = """
            SELECT COUNTRY_CODE, YEAR, INDICATOR, VALUE, SOURCE
            FROM MACRO_INDICATORS
            WHERE COUNTRY_CODE = %s
            ORDER BY YEAR, INDICATOR
            """
            
            cursor.execute(query, (country_code,))
            rows = cursor.fetchall()
            
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No macro indicators found for country code: {country_code}"
                )
            
            # Convert rows to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            records = [convert_snowflake_row_to_dict(row, columns) for row in rows]
            
            cursor.close()
        
        return {
            "country_code": country_code,
            "count": len(records),
            "data": records
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching macro indicators from Snowflake: {str(e)}")


@app.get("/companies")
async def get_companies():
    """
    Get all company financials data from Snowflake.
    Source of truth: Snowflake COMPANY_FINANCIALS table.
    
    Returns:
        JSON response with count and data array of company financial records
    """
    try:
        with snowflake_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Direct query - no parameters needed for full table scan
            query = """
            SELECT COMPANY, YEAR, REVENUE_USD, NET_INCOME_USD
            FROM COMPANY_FINANCIALS
            ORDER BY COMPANY, YEAR
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                return {
                    "count": 0,
                    "data": []
                }
            
            # Convert rows to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            records = [convert_snowflake_row_to_dict(row, columns) for row in rows]
            
            cursor.close()
        
        return {
            "count": len(records),
            "data": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company financials from Snowflake: {str(e)}")


@app.get("/forecasts/{company}")
async def get_forecasts(company: str):
    """
    Get forecasts for a specific company from Snowflake.
    Source of truth: Snowflake FORECASTS table.
    
    Args:
        company: Company name (e.g., 'Apple', 'Samsung')
    
    Returns:
        JSON response with company, count, and data array of forecast records
    """
    try:
        with snowflake_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Parameterized query to prevent SQL injection
            query = """
            SELECT ENTITY_TYPE, ENTITY_NAME, YEAR, FORECAST_VALUE, MODEL_USED
            FROM FORECASTS
            WHERE ENTITY_NAME = %s AND ENTITY_TYPE = 'company_revenue'
            ORDER BY YEAR, MODEL_USED
            """
            
            cursor.execute(query, (company,))
            rows = cursor.fetchall()
            
            if not rows:
                # Return empty response instead of 404 to allow graceful handling
                return {
                    "company": company,
                    "count": 0,
                    "data": []
                }
            
            # Convert rows to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            records = [convert_snowflake_row_to_dict(row, columns) for row in rows]
            
            cursor.close()
        
        return {
            "company": company,
            "count": len(records),
            "data": records
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecasts from Snowflake: {str(e)}")


# ============================================================================
# Snowflake Endpoints
# ============================================================================

@app.get("/snowflake/macro/{country_code}")
async def get_snowflake_macro_indicators(country_code: str):
    """
    Get macro indicators for a specific country from Snowflake (using connection pool).
    This endpoint is an alias for /macro/{country_code} for backward compatibility.
    
    Args:
        country_code: ISO country code (e.g., 'IND', 'BRA')
    
    Returns:
        List of macro indicator records from Snowflake
    """
    # Delegate to main endpoint
    return await get_macro_indicators(country_code)


@app.get("/snowflake/companies")
async def get_snowflake_companies():
    """
    Get all company financials data from Snowflake (using connection pool).
    This endpoint is an alias for /companies for backward compatibility.
    
    Returns:
        List of company financial records from Snowflake
    """
    # Delegate to main endpoint
    return await get_companies()


@app.get("/snowflake/forecasts/{company}")
async def get_snowflake_forecasts(company: str):
    """
    Get forecasts for a specific company from Snowflake (using connection pool).
    This endpoint is an alias for /forecasts/{company} for backward compatibility.
    
    Args:
        company: Company name (e.g., 'Apple', 'Samsung')
    
    Returns:
        List of forecast records for the company from Snowflake
    """
    # Delegate to main endpoint
    return await get_forecasts(company)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connection pool on shutdown."""
    try:
        snowflake_pool.close_all()
        logger.info("Snowflake connection pool closed")
    except Exception as e:
        logger.warning(f"Error closing connection pool: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable, default to 8000
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT", "production").lower() != "production"
    
    uvicorn.run(app, host=host, port=port, reload=reload)
