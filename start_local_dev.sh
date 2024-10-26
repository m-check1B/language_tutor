#!/bin/bash

# Start PostgreSQL in Docker
echo "Starting PostgreSQL database..."
docker compose -f docker-compose.yml up -d db

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 10  # Give more time for PostgreSQL to initialize

# Install required packages
echo "Installing required packages..."
cd backend
pip install deepgram-sdk==2.12.0
cd ..

# Start services with PM2
echo "Starting services with PM2..."
pm2 delete all 2>/dev/null
pm2 start ecosystem.config.js

echo "Local development environment is ready!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Database: localhost:5432"
echo ""
echo "Use 'pm2 logs' to view logs"
echo "Use 'pm2 stop all' to stop services"
