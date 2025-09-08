@echo off
echo Starting NGINX Gateway with Docker...

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Create network if it doesn't exist
echo Creating microservices network...
docker network create microservices-network 2>nul

REM Build and start NGINX gateway
echo Building NGINX Gateway image...
docker-compose build

echo Starting NGINX Gateway container...
docker-compose up -d

REM Wait for container to be ready
echo Waiting for NGINX Gateway to be ready...
timeout /t 10 /nobreak > nul

REM Check health
docker-compose ps
curl -f http://localhost:8080/health > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo NGINX Gateway started successfully with Docker!
    echo ================================
    echo Gateway URL: http://localhost:8080
    echo Health Check: http://localhost:8080/health
    echo Eureka Dashboard: http://localhost:8080/eureka/
    echo ================================
    echo.
    echo To view logs: docker-compose logs -f
    echo To stop: docker-compose down
    echo ================================
) else (
    echo.
    echo Failed to start NGINX Gateway or health check failed.
    echo Check container logs: docker-compose logs
)

pause
