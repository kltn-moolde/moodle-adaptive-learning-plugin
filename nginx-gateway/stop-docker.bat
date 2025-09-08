@echo off
echo Stopping NGINX Gateway Docker containers...

REM Stop and remove containers
docker-compose down

REM Optional: Remove images (uncomment if needed)
REM docker-compose down --rmi all

REM Show status
echo.
echo Docker containers stopped.
echo.
echo To remove all data: docker-compose down -v
echo To remove network: docker network rm microservices-network

pause
