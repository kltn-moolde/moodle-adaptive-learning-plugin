@echo off
echo Stopping NGINX Gateway...

REM Stop NGINX gracefully
nginx -s quit 2>nul

REM Force kill if graceful stop failed
timeout /t 2 /nobreak > nul
tasklist | find "nginx.exe" > nul
if %ERRORLEVEL% EQU 0 (
    echo Forcing NGINX shutdown...
    taskkill /IM nginx.exe /F 2>nul
)

REM Check if stopped
timeout /t 1 /nobreak > nul
tasklist | find "nginx.exe" > nul
if %ERRORLEVEL% NEQ 0 (
    echo NGINX Gateway stopped successfully.
) else (
    echo Warning: Some NGINX processes may still be running.
)

pause
