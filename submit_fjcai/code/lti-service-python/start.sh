#!/bin/bash

# LTI Service Python - Startup Script
# This script sets up and starts the Python LTI service

set -e

echo "🐍 Starting LTI Service Python..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python version: $python_version"
}

# Check if pip is installed
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p data
    print_success "Directories created"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    # Database will be initialized automatically when the app starts
    print_success "Database initialization will happen on first run"
}

# Start the service
start_service() {
    print_status "Starting LTI Service Python..."
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        print_warning ".env file not found. Using default configuration."
    fi
    
    # Start the service
    if [[ "$1" == "--dev" ]]; then
        print_status "Starting in development mode with auto-reload..."
        uvicorn main:app --host 0.0.0.0 --port 8082 --reload
    else
        print_status "Starting in production mode..."
        uvicorn main:app --host 0.0.0.0 --port 8082
    fi
}

# Main function
main() {
    print_status "LTI Service Python Setup"
    print_status "========================"
    
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    create_directories
    init_database
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    print_status "Starting service..."
    start_service "$1"
}

# Handle script arguments
case "$1" in
    --dev)
        main --dev
        ;;
    --help|-h)
        echo "LTI Service Python Startup Script"
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --dev     Start in development mode with auto-reload"
        echo "  --help    Show this help message"
        echo ""
        exit 0
        ;;
    *)
        main
        ;;
esac
