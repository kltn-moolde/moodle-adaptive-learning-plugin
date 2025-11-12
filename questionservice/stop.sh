#!/bin/bash
# Stop Question Service

echo "Stopping Question Service..."

# Find and kill gunicorn processes
pkill -f "gunicorn.*app:create_app" && echo "✓ Service stopped" || echo "✗ Service not running"
