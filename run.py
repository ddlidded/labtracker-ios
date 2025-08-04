#!/usr/bin/env python3
"""
Startup script for the Mass Spec Pressure Analyzer application.
"""

import os
import sys
from app import app

def main():
    """Main function to start the Flask application."""
    print("=" * 60)
    print("Thermo Mass Spec Pressure Analyzer")
    print("=" * 60)
    print("Starting application...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Run the Flask application with optimized settings for large files
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True,
            # Increase timeout for large file uploads
            request_timeout=3600,  # 1 hour timeout
            # Enable request buffering for large files
            request_buffer_size=2 * 1024 * 1024 * 1024  # 2GB buffer
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()