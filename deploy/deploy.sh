#!/bin/bash
# Deploy script for Adaptive Learning Platform
# Run this on the server to deploy latest version

set -e

echo "🚀 Deploying Adaptive Learning Platform..."

# Navigate to application directory
cd /opt/adaptive-learning

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Pull latest Docker images
echo "🐳 Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

# Start services with new images
echo "▶️ Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🔍 Running health checks..."
echo "=== Kong Gateway ==="
curl -f http://localhost:8000 || echo "❌ Kong Gateway not ready"

echo "=== User Service ==="
curl -f http://localhost:8080/auth/health || echo "❌ User Service not ready"

echo "=== LTI Service ==="
curl -f http://localhost:8082/health || echo "❌ LTI Service not ready"

echo "=== Frontend Service ==="
curl -f http://localhost:5173 || echo "❌ Frontend Service not ready"

# Show running containers
echo "📋 Running containers:"
docker-compose -f docker-compose.prod.yml ps

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment completed!"
echo ""
echo "🔗 Services are available at:"
echo "   - Frontend: http://51.68.124.207"
echo "   - API Gateway: http://51.68.124.207/api/"
echo "   - User Service: http://51.68.124.207/auth/"
echo "   - LTI Service: http://51.68.124.207/lti/"