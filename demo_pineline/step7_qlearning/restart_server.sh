#!/bin/bash
# Restart Q-Learning API Server with CORS enabled

echo "🔄 Restarting Q-Learning API Server..."
echo "📍 Location: step7_qlearning"
echo "🌐 Port: 8080"
echo "✅ CORS: Enabled for http://localhost:5173"
echo ""

cd "$(dirname "$0")"

# Kill existing process on port 8080
echo "🔍 Checking for existing process on port 8080..."
EXISTING_PID=$(lsof -ti:8080)
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️  Found existing process (PID: $EXISTING_PID)"
    echo "🔪 Killing process..."
    kill -9 $EXISTING_PID 2>/dev/null
    sleep 1
    echo "✅ Process killed"
else
    echo "✅ No existing process found"
fi

echo ""
echo "🚀 Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start server
uvicorn api_service:app --reload --port 8080

# Note: If you see an error about uvicorn not found, activate venv first:
# source /path/to/.venv/bin/activate
