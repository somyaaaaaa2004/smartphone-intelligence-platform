"""
Gunicorn configuration file for production deployment.
This file configures Gunicorn to run FastAPI with Uvicorn workers.
"""
import multiprocessing
import os

# Server socket
# Use PORT from environment (required by cloud platforms like Railway, Render, Heroku)
port = int(os.getenv('PORT', '8000'))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
# Use Uvicorn workers for async FastAPI support
worker_class = "uvicorn.workers.UvicornWorker"
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_connections = 1000
keepalive = 5

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # "-" means stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")  # "-" means stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "smartphone-intelligence-api"

# Server mechanics
daemon = False
pidfile = os.getenv("GUNICORN_PIDFILE", None)
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed - uncomment and configure)
# keyfile = "/path/to/keyfile.pem"
# certfile = "/path/to/certfile.pem"

# Performance tuning
max_requests = 1000  # Restart worker after this many requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to max_requests to prevent all workers restarting at once
preload_app = True  # Load application code before forking workers

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Worker timeout (should be higher than FastAPI request timeout)
# This is the maximum time a worker can take to process a request
timeout = 60

# Enable statsd (optional - for monitoring)
# statsd_host = "localhost:8125"
# statsd_prefix = "smartphone_intelligence_api"
