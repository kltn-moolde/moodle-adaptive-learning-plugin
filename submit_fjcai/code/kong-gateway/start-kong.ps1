# Kong Gateway Startup Script for Windows
# Run this script in PowerShell

Write-Host "🚀 Starting Kong Gateway and all services..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose-local.yml down

# Start all services
Write-Host "📦 Starting Kong Gateway..." -ForegroundColor Cyan
docker-compose -f docker-compose-local.yml up -d

# Wait for Kong to be ready
Write-Host "⏳ Waiting for Kong Gateway to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Configure Kong
Write-Host "🔧 Configuring Kong Gateway..." -ForegroundColor Blue
PowerShell -ExecutionPolicy Bypass -File ".\configure-kong.ps1"

Write-Host ""
Write-Host "✅ Kong Gateway is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Quick Links:" -ForegroundColor Blue
Write-Host "   🌐 Gateway:          http://localhost:8000" -ForegroundColor White
Write-Host "   ⚙️  Admin API:       http://localhost:8001" -ForegroundColor White
Write-Host "   🎨 Admin GUI:        http://localhost:8002" -ForegroundColor White
Write-Host "   📊 Konga UI:         http://localhost:1337" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Test your setup:" -ForegroundColor Blue
Write-Host "   Invoke-RestMethod http://localhost:8000/auth/health" -ForegroundColor White
Write-Host ""
