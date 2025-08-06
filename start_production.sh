#!/bin/bash

# Production startup script for Mass Spec Pressure Analyzer
# Optimized for large file uploads (up to 2GB)

echo "============================================================"
echo "Thermo Mass Spec Pressure Analyzer - Production Server"
echo "============================================================"

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn..."
    pip3 install gunicorn
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Set environment variables for large file uploads
export PYTHONUNBUFFERED=1
export FLASK_ENV=production

echo "Starting production server with Gunicorn..."
echo "Server will be available at: http://localhost:5000"
echo "Maximum file upload size: 2GB"
echo "Press Ctrl+C to stop the server"
echo "============================================================"

# Start Gunicorn with optimized settings for large files
gunicorn \
    --config gunicorn.conf.py \
    --worker-class sync \
    --workers 4 \
    --timeout 3600 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:application