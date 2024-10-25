#!/bin/sh

# Function to wait for the database to be ready
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z db 5432; do
        sleep 0.1
    done
    echo "Database is ready!"
}

# Install netcat for database connection check
apt-get update && apt-get install -y netcat-openbsd

# Wait for the database
wait_for_db

# Create tables
echo "Creating database tables..."
PYTHONPATH=/app python -c "
from app.database import Base, sync_engine
from app import models
Base.metadata.create_all(bind=sync_engine)
"

# Run migrations
echo "Running database migrations..."
PYTHONPATH=/app alembic upgrade head

# Start the application
echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
