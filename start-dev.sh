#!/bin/bash

# CareerCraft AI Development Server Starter
# Usage: ./start-dev.sh [backend_port] [frontend_port]
# Example: ./start-dev.sh 8080 3001

# Default ports
BACKEND_PORT=${1:-8000}
FRONTEND_PORT=${2:-3000}

echo "🚀 Starting CareerCraft AI Development Environment"
echo "📡 Backend port: $BACKEND_PORT"
echo "🌐 Frontend port: $FRONTEND_PORT"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up cleanup on script exit
trap cleanup SIGINT SIGTERM

# Check if .env.local exists
if [ ! -f "frontend/.env.local" ]; then
    echo "⚠️  Warning: frontend/.env.local not found"
    echo "   Run 'python backend/setup.py' first to configure the application"
    echo ""
fi

# Start backend
echo "🐍 Starting Python backend on port $BACKEND_PORT..."
cd backend
python main.py --port $BACKEND_PORT --host 127.0.0.1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Update frontend env to point to correct backend port
echo "⚛️  Configuring frontend for backend port $BACKEND_PORT..."
if [ -f "frontend/.env.local" ]; then
    # Update the API base URL in .env.local
    sed -i.bak "s|REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=http://localhost:$BACKEND_PORT|" frontend/.env.local
fi

# Start frontend
echo "⚛️  Starting React frontend on port $FRONTEND_PORT..."
cd frontend
PORT=$FRONTEND_PORT npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development servers started successfully!"
echo "📡 Backend API: http://localhost:$BACKEND_PORT"
echo "🌐 Frontend UI: http://localhost:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID