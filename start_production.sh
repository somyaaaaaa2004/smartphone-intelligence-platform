#!/bin/bash
# Production startup script for Smartphone Intelligence Platform API
# This script starts the API using Gunicorn with production settings

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Smartphone Intelligence Platform API...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated.${NC}"
    echo "It's recommended to use a virtual environment in production."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${RED}ERROR: gunicorn not found!${NC}"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required Snowflake variables
REQUIRED_VARS=("SNOWFLAKE_ACCOUNT" "SNOWFLAKE_USER" "SNOWFLAKE_PASSWORD" "SNOWFLAKE_WAREHOUSE" "SNOWFLAKE_DATABASE")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}ERROR: Missing required environment variables:${NC}"
    printf '%s\n' "${MISSING_VARS[@]}"
    exit 1
fi

# Set defaults if not set
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}
export API_HOST=${API_HOST:-0.0.0.0}

echo -e "${GREEN}Configuration:${NC}"
echo "  Port: $PORT"
echo "  Host: $API_HOST"
echo "  Environment: $ENVIRONMENT"
echo "  Workers: ${GUNICORN_WORKERS:-auto}"

# Start Gunicorn
echo -e "${GREEN}Starting Gunicorn server...${NC}"
exec gunicorn backend.main:app -c gunicorn.conf.py
