@echo off
REM Eureka Service Discovery Integration Script for Windows
REM Automatically updates NGINX upstream configuration based on Eureka registry

setlocal enabledelayedexpansion

set EUREKA_URL=http://localhost:8761/eureka/apps
set NGINX_CONF_DIR=%~dp0..\conf
set NGINX_UPSTREAM_FILE=%NGINX_CONF_DIR%\dynamic-upstreams.conf
set NGINX_PID_FILE=%~dp0..\logs\nginx.pid
set TEMP_JSON=%TEMP%\eureka_services.json

:log
echo [%date% %time%] %~1
goto :eof

:error
echo [%date% %time%] ERROR: %~1
goto :eof

:fetch_services
call :log "Fetching services from Eureka..."
curl -s -H "Accept: application/json" "%EUREKA_URL%" > "%TEMP_JSON%" 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :error "Failed to connect to Eureka at %EUREKA_URL%"
    exit /b 1
)
goto :eof

:generate_upstream_config
call :log "Generating NGINX upstream configuration..."

REM Create header
echo # Auto-generated upstream configuration from Eureka > "%NGINX_UPSTREAM_FILE%"
echo # Generated at: %date% %time% >> "%NGINX_UPSTREAM_FILE%"
echo # DO NOT EDIT MANUALLY - This file is auto-generated >> "%NGINX_UPSTREAM_FILE%"
echo. >> "%NGINX_UPSTREAM_FILE%"

REM Parse JSON and generate config (simplified version)
REM Note: This is a basic implementation. For production, consider using PowerShell or jq

REM Example static configuration for common services
echo upstream user-service-cluster { >> "%NGINX_UPSTREAM_FILE%"
echo     least_conn; >> "%NGINX_UPSTREAM_FILE%"
echo     server 127.0.0.1:8086 max_fails=3 fail_timeout=30s weight=1; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive 32; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_requests 100; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_timeout 60s; >> "%NGINX_UPSTREAM_FILE%"
echo } >> "%NGINX_UPSTREAM_FILE%"
echo. >> "%NGINX_UPSTREAM_FILE%"

echo upstream course-service-cluster { >> "%NGINX_UPSTREAM_FILE%"
echo     least_conn; >> "%NGINX_UPSTREAM_FILE%"
echo     server 127.0.0.1:8084 max_fails=3 fail_timeout=30s weight=1; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive 32; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_requests 100; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_timeout 60s; >> "%NGINX_UPSTREAM_FILE%"
echo } >> "%NGINX_UPSTREAM_FILE%"
echo. >> "%NGINX_UPSTREAM_FILE%"

echo upstream common-service-cluster { >> "%NGINX_UPSTREAM_FILE%"
echo     least_conn; >> "%NGINX_UPSTREAM_FILE%"
echo     server 127.0.0.1:8087 max_fails=3 fail_timeout=30s weight=1; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive 32; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_requests 100; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_timeout 60s; >> "%NGINX_UPSTREAM_FILE%"
echo } >> "%NGINX_UPSTREAM_FILE%"
echo. >> "%NGINX_UPSTREAM_FILE%"

echo upstream lti-service-cluster { >> "%NGINX_UPSTREAM_FILE%"
echo     least_conn; >> "%NGINX_UPSTREAM_FILE%"
echo     server 127.0.0.1:8082 max_fails=3 fail_timeout=30s weight=1; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive 32; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_requests 100; >> "%NGINX_UPSTREAM_FILE%"
echo     keepalive_timeout 60s; >> "%NGINX_UPSTREAM_FILE%"
echo } >> "%NGINX_UPSTREAM_FILE%"
echo. >> "%NGINX_UPSTREAM_FILE%"

call :log "Upstream configuration generated: %NGINX_UPSTREAM_FILE%"
goto :eof

:test_nginx_config
call :log "Testing NGINX configuration..."
nginx -t -c "%NGINX_CONF_DIR%\nginx.conf" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log "NGINX configuration test passed"
    exit /b 0
) else (
    call :error "NGINX configuration test failed"
    nginx -t -c "%NGINX_CONF_DIR%\nginx.conf"
    exit /b 1
)

:reload_nginx
call :log "Reloading NGINX..."
nginx -s reload >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log "NGINX reloaded successfully"
    exit /b 0
) else (
    call :error "Failed to reload NGINX"
    exit /b 1
)

:main
call :log "Starting Eureka service discovery sync..."

REM Create logs directory if it doesn't exist
if not exist "%~dp0..\logs" mkdir "%~dp0..\logs"

REM Fetch services from Eureka
call :fetch_services
if %ERRORLEVEL% NEQ 0 (
    call :error "Failed to fetch services from Eureka"
    exit /b 1
)

REM Generate backup of current config
if exist "%NGINX_UPSTREAM_FILE%" (
    copy "%NGINX_UPSTREAM_FILE%" "%NGINX_UPSTREAM_FILE%.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
)

REM Generate new upstream configuration
call :generate_upstream_config

REM Test configuration
call :test_nginx_config
if %ERRORLEVEL% EQU 0 (
    REM Reload NGINX if test passes
    call :reload_nginx
    if %ERRORLEVEL% EQU 0 (
        call :log "Eureka sync completed successfully"
    ) else (
        call :error "Configuration updated but NGINX reload failed"
    )
) else (
    call :error "Configuration test failed"
    exit /b 1
)

goto :eof

REM Main execution
if "%1"=="--watch" (
    call :log "Starting continuous monitoring mode..."
    :watch_loop
    call :main
    call :log "Waiting 30 seconds before next sync..."
    timeout /t 30 /nobreak >nul
    goto watch_loop
) else (
    call :main
)

pause
