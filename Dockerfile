# Dockerfile for Streamlit Dashboard on Render
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
# gcc, g++ are needed for snowflake-connector-python and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render sets PORT dynamically)
EXPOSE 8501

# Health check for Streamlit (uses default port 8501)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit on Render
# PORT is set by Render environment variable
# Use sh -c to allow environment variable substitution
CMD sh -c "streamlit run dashboard/app.py --server.port=\${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"
