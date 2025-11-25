#!/bin/bash
# Check Question Service status

echo "Question Service Status:"
echo "======================="

# Check if process is running
if pgrep -f "gunicorn.*app:create_app" > /dev/null; then
    echo "✓ Service is RUNNING"
    echo ""
    echo "Processes:"
    ps aux | grep "[g]unicorn.*app:create_app" | awk '{print "  PID: " $2 " - CPU: " $3 "% - MEM: " $4 "%"}'
    echo ""
    echo "Listening on port 5003:"
    lsof -i :5003 2>/dev/null | grep LISTEN || echo "  (checking...)"
else
    echo "✗ Service is NOT running"
fi

echo ""
echo "Commands:"
echo "  Start:   ./start.sh"
echo "  Stop:    ./stop.sh"  
echo "  Restart: ./restart.sh"
echo "  Status:  ./status.sh"
