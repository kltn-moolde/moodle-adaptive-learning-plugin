#!/bin/bash

# Question Service Startup Script
# =================================

echo "========================================="
echo "Question Service - Startup"
echo "========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Create logs directory
mkdir -p logs

# Start service with Gunicorn
echo "========================================="
echo "Starting Question Service with Gunicorn..."
echo "========================================="
echo "Service will run on: http://0.0.0.0:5003"
echo ""

# Run with Gunicorn using config file
gunicorn -c gunicorn.conf.py "app:create_app()"
