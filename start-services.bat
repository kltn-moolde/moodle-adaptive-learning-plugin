@echo off
echo Starting Microservices Architecture...

echo.
echo ====================================
echo 1. Starting Discovery Service (Eureka)
echo ====================================
cd discoveryservice
start "Discovery Service" cmd /k "mvn spring-boot:run"
echo Waiting for Discovery Service to start...
timeout /t 30 /nobreak

echo.
echo ====================================
echo 2. Starting Gateway Service
echo ====================================
cd ..\gatewayservice
start "Gateway Service" cmd /k "mvn spring-boot:run"
echo Waiting for Gateway Service to start...
timeout /t 15 /nobreak

echo.
echo ====================================
echo 3. Starting Other Services
echo ====================================

echo Starting User Service...
cd ..\userservice
start "User Service" cmd /k "mvn spring-boot:run"
timeout /t 5 /nobreak

echo Starting Course Service...
cd ..\courseservice
start "Course Service" cmd /k "mvn spring-boot:run"
timeout /t 5 /nobreak

echo Starting Common Service...
cd ..\commonservice
start "Common Service" cmd /k "mvn spring-boot:run"
timeout /t 5 /nobreak

echo Starting LTI Plugin Service...
cd ..\plugin-moodle-LTI-1.3
start "LTI Service" cmd /k "mvn spring-boot:run"

echo.
echo ====================================
echo All services are starting...
echo ====================================
echo Discovery Service: http://localhost:8761
echo Gateway Service: http://localhost:8080
echo User Service: will register with Eureka
echo Course Service: will register with Eureka
echo Common Service: will register with Eureka
echo LTI Service: will register with Eureka
echo.
echo Check Eureka Dashboard at: http://localhost:8761
echo ====================================

pause
