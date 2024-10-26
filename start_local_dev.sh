#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Function to kill processes using specific ports
kill_port() {
    local port=$1
    if command_exists lsof; then
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
    fi
}

# Check for required commands
command_exists node || handle_error "Node.js is not installed"
command_exists npm || handle_error "npm is not installed"
command_exists python || handle_error "Python is not installed"

# Kill any processes using our ports
echo "Cleaning up existing processes..."
kill_port 8001
kill_port 5173
kill_port 5174

# Create and activate Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv || handle_error "Failed to create virtual environment"
fi

# Activate virtual environment
source venv/bin/activate || handle_error "Failed to activate virtual environment"

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt || handle_error "Failed to install backend dependencies"

# Run database migrations
echo "Running database migrations..."
PYTHONPATH=/home/matej/github/full_system/language_tutor/backend alembic upgrade head || handle_error "Failed to run migrations"

# Update frontend environment with new backend port
cd ../frontend
echo "VITE_API_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001
VITE_ENABLE_AUDIO=true
VITE_ENABLE_VIDEO=true
VITE_ENABLE_IMAGE=true
VITE_ENABLE_PDF=true
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_TTS=true
VITE_DEFAULT_LOCALE=en
VITE_SUPPORTED_LOCALES=en,cs,es" > .env

# Start backend
echo "Starting backend..."
cd ../backend
PYTHONPATH=/home/matej/github/full_system/language_tutor/backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd ../frontend
npm install || handle_error "Failed to install frontend dependencies"

# Start frontend
echo "Starting frontend..."
npm run dev -- --host &
FRONTEND_PID=$!

# Handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    deactivate
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
echo "Development environment is ready!"
echo "Backend running on http://localhost:8001"
echo "Frontend running on http://localhost:5173 or http://localhost:5174"
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
