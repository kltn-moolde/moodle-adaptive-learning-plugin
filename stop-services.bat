@echo off
echo Stopping all microservices...

echo Stopping Spring Boot applications on common ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8761"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8082"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8084"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8086"') do taskkill /PID %%a /F 2>nul

echo Stopping cmd windows with service names...
taskkill /FI "WINDOWTITLE eq Discovery Service*" /F 2>nul
taskkill /FI "WINDOWTITLE eq Gateway Service*" /F 2>nul
taskkill /FI "WINDOWTITLE eq User Service*" /F 2>nul
taskkill /FI "WINDOWTITLE eq Course Service*" /F 2>nul
taskkill /FI "WINDOWTITLE eq Common Service*" /F 2>nul
taskkill /FI "WINDOWTITLE eq LTI Service*" /F 2>nul

echo All services stopped.
pause
