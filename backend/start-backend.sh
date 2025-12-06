#!/bin/bash

# Quick Backend Test Script
echo "🧪 Testing Backend Server..."

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
source ../venv/bin/activate

# Install requirements
echo "📥 Installing/updating dependencies..."
pip install -q -r requirements.txt

# Start server
echo "🚀 Starting backend server..."
python server.py
