#!/bin/bash

# SouqPilot Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting SouqPilot..."

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "OPENAI_API_KEY=your_key_here"
    echo ""
fi

# Start backend server in the background
echo "🔧 Starting backend server on port 8000..."
cd backend
python server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ SouqPilot is running!"
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
