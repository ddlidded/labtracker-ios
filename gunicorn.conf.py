# Gunicorn configuration for Mass Spec Pressure Analyzer
# Optimized for large file uploads (up to 2GB)

import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Timeout settings for large file uploads
timeout = 3600  # 1 hour
keepalive = 2
graceful_timeout = 3600

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "mass-spec-analyzer"

# Server mechanics
daemon = False
pidfile = "/tmp/mass-spec-analyzer.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Large file upload settings
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files
forwarded_allow_ips = "*"

# Memory management
max_requests = 1000
max_requests_jitter = 50

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190