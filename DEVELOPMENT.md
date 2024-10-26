# Development Guide

This guide explains how to set up the development environment for the Language Tutor application.

## Architecture Overview

The application uses a flexible development setup that allows you to:
- Run the database in Docker
- Run the backend and frontend either locally or in Docker
- Mix and match components as needed during development

## Getting Started

### 1. Database Setup

First, start the PostgreSQL database using Docker:

```bash
docker-compose up db
```

This will:
- Start PostgreSQL 16.1 on port 5432
- Create a persistent volume for data storage
- Set up a bridge network for container communication
- **Make the database accessible at localhost:5432**

To verify the database is accessible from your local environment:
```bash
python local_dev_test.py
```

### 2. Backend Setup

#### Local Development
1. Copy `.env.example` to `.env` in the backend directory:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Ensure these settings in your `.env` file for local development:
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

3. Install dependencies and run the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install psycopg2-binary  # Required for database connectivity
   uvicorn app.main:app --reload
   ```

#### Docker Development
1. Set `POSTGRES_HOST=db` in your `.env` file
2. Run `docker-compose up backend`

### 3. Frontend Setup

#### Local Development
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

#### Docker Development
```bash
docker-compose up frontend
```

## Development Workflow

### Database Access
- From local machine: `localhost:5432`
  - Username: postgres
  - Password: postgres
  - Database: language_tutor
- From Docker containers: `db:5432`

### API Access
- Backend URL: `http://localhost:8000`
- Frontend development server: `http://localhost:3000`

## Troubleshooting

### Database Connection
1. Ensure the database container is running:
   ```bash
   docker ps | grep postgres
   ```

2. Verify port mapping:
   ```bash
   docker-compose ps db
   ```
   Should show port 5432 mapped to host

3. Test connection:
   ```bash
   python local_dev_test.py
   ```

4. Common issues:
   - If port 5432 is already in use, stop any local PostgreSQL instance
   - Check if the database container is healthy using `docker-compose ps`
   - Verify your .env file has the correct host settings

## Tips
- Use the Docker database with local development for faster iteration
- The bridge network allows Docker containers to communicate using service names
- Environment variables in `.env` control the configuration
- Hot-reload is enabled for both frontend and backend in local development
