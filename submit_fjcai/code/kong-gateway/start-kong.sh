#!/bin/bash

# Kong Gateway Startup Script
set -e

echo "🚀 Starting Kong Gateway and all services..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start all services
echo "📦 Starting all services..."
docker-compose up -d

# Wait for Kong to be ready
echo "⏳ Waiting for Kong Gateway to start..."
sleep 30

# Configure Kong
echo "🔧 Configuring Kong Gateway..."
chmod +x configure-kong.sh
./configure-kong.sh

echo ""
echo "✅ Kong Gateway is ready!"
echo ""
echo "📋 Quick Links:"
echo "   🌐 Gateway:          http://localhost:8000"
echo "   ⚙️  Admin API:       http://localhost:8001"
echo "   🎨 Admin GUI:        http://localhost:8002"
echo "   📊 Konga UI:         http://localhost:1337"
echo ""
echo "🎯 Test your setup:"
echo "   curl http://localhost:8000/auth/health"
echo ""
