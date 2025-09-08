@echo off
echo Starting NGINX Gateway...

REM Check if NGINX is installed
where nginx >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo NGINX is not installed or not in PATH.
    echo Please install NGINX first or use Docker.
    echo.
    echo Option 1: Install NGINX for Windows
    echo Download from: http://nginx.org/en/download.html
    echo.
    echo Option 2: Use Docker
    echo Run: docker-compose up -d
    pause
    exit /b 1
)

REM Initialize Eureka service discovery
echo Initializing service discovery...
call "%~dp0scripts\eureka-sync.bat"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Eureka sync failed, using default configuration
)

REM Check NGINX configuration
echo Checking NGINX configuration...
nginx -t -c "%~dp0conf\nginx.conf"
if %ERRORLEVEL% NEQ 0 (
    echo NGINX configuration test failed!
    pause
    exit /b 1
)

REM Start NGINX
echo Starting NGINX with custom configuration...
start "NGINX Gateway" nginx -c "%~dp0conf\nginx.conf"

REM Start Eureka sync in background (optional)
echo Starting background service discovery...
start "Eureka Sync" "%~dp0scripts\eureka-sync.bat" --watch

REM Check if NGINX started successfully
timeout /t 3 /nobreak > nul
curl -f http://localhost:8080/health > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo NGINX Gateway started successfully!
    echo ================================
    echo Gateway URL: http://localhost:8080
    echo Health Check: http://localhost:8080/health
    echo Eureka Dashboard: http://localhost:8080/eureka/
    echo NGINX Status: http://localhost:8081/nginx_status
    echo ================================
    echo.
    echo Background services:
    echo - NGINX Gateway (port 8080)
    echo - Eureka Service Discovery Sync
    echo ================================
) else (
    echo.
    echo Failed to start NGINX Gateway or health check failed.
    echo Check the logs for more information.
)

pause
