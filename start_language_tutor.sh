#!/bin/bash

# Check if user has Docker permissions
if ! groups | grep -q '\bdocker\b'; then
    echo "Error: Current user doesn't have permission to use Docker."
    echo "To fix this, run the following commands:"
    echo "sudo usermod -aG docker $USER"
    echo "newgrp docker"
    echo "Then log out and log back in, or restart your computer."
    echo "After that, run this script again."
    exit 1


# Set up environment variables
echo "Setting up environment variables..."
export DB_USER=language_tutor_user
export DB_PASSWORD=your_secure_password
export DB_NAME=language_tutor_db
export BACKEND_SECRET_KEY=your_backend_secret_key
export OPENAI_API_KEY=your_openai_api_key
export GOOGLE_CLIENT_ID=your_google_client_id
export GOOGLE_CLIENT_SECRET=your_google_client_secret

# Stop and remove existing containers
echo "Stopping and removing existing containers..."
docker-compose down

# Remove all unused containers, networks, images (both dangling and unreferenced), and volumes
echo "Cleaning up Docker system..."
docker system prune -af --volumes

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Provide instructions
echo "
Language Tutor application has been cleaned, rebuilt, and restarted!

Access the application:
- Frontend: http://localhost:3081
- Backend API: http://localhost:8081

To stop the application, run:
docker-compose down

Enjoy using Language Tutor!
"
