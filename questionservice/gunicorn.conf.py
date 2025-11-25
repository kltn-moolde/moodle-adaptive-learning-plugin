# Gunicorn Configuration File
# Place this in the root directory as gunicorn.conf.py

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5003"
backlog = 2048

# Worker processes
workers = 4  # Fixed to 4 workers
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging - output to stdout/stderr
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "questionservice"

# Preload app for better performance
preload_app = True

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment - Comment out to use defaults from config.py
# Only set raw_env if you have actual environment variables
# raw_env = [
#     f"MONGO_URI={os.getenv('MONGO_URI', '')}",
#     f"GEMINI_API_KEY={os.getenv('GEMINI_API_KEY', '')}",
# ]

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Question Service is starting...")

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("🔄 Question Service is reloading...")

def when_ready(server):
    """Called just after the server is started."""
    print("✅ Question Service is ready to serve requests!")

def on_exit(server):
    """Called just before exiting."""
    print("👋 Question Service is shutting down...")
