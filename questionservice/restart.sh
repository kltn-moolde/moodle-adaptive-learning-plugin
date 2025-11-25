#!/bin/bash
# Restart Question Service

echo "Restarting Question Service..."

# Stop if running
./stop.sh

# Wait a bit
sleep 1

# Start again
./start.sh &
