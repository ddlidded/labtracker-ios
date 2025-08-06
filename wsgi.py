#!/usr/bin/env python3
"""
WSGI configuration for production deployment of the Mass Spec Pressure Analyzer.
This file is used for production servers like Gunicorn or uWSGI.
"""

import os
import sys
from app import app

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Production configuration
if __name__ == "__main__":
    # For development server
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        debug=False  # Set to False for production
    )
else:
    # For WSGI servers (Gunicorn, uWSGI, etc.)
    # The app object is imported by the WSGI server
    pass

# WSGI application object
application = app