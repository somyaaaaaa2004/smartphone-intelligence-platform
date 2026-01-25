# PythonAnywhere configuration
# This file helps with PythonAnywhere deployment
# Note: PythonAnywhere uses WSGI, not ASGI directly

# For PythonAnywhere, you'll need to create a WSGI file
# Create a file: /var/www/yourusername_pythonanywhere_com_wsgi.py
# with this content:

"""
import sys
import os

# Add your project directory to the path
path = '/home/yourusername/smartphone-intelligence-platform'
if path not in sys.path:
    sys.path.insert(0, path)

# Change to your project directory
os.chdir(path)

# Import the FastAPI app
from backend.main import app

# PythonAnywhere uses WSGI, so we need to use a WSGI adapter
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.serving import run_simple

application = WSGIMiddleware(app)
"""
