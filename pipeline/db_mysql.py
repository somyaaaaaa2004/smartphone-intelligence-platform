"""
MySQL database connection module using SQLAlchemy.
Reads database credentials from .env file.
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_mysql_engine():
    """
    Create and return a SQLAlchemy engine for MySQL connection.
    
    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine instance
    """
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3306')
    database = os.getenv('MYSQL_DB', 'smartphone_intelligence')
    user = os.getenv('MYSQL_USER', 'app_user')
    password = os.getenv('MYSQL_PASSWORD', '')
    
    # URL-encode password to handle special characters like @
    encoded_password = quote_plus(password)
    
    # Construct MySQL connection URL
    connection_url = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
    
    # Create engine with connection pooling
    engine = create_engine(
        connection_url,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False           # Set to True for SQL query logging
    )
    
    return engine

def get_mysql_session():
    """
    Create and return a SQLAlchemy session.
    
    Returns:
        sqlalchemy.orm.Session: SQLAlchemy session instance
    """
    engine = get_mysql_engine()
    Session = sessionmaker(bind=engine)
    return Session()
