# Language Tutor Application

This is a Language Tutor application that helps users improve their language skills through AI-powered conversations.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

To run the Language Tutor application, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd language_tutor
   ```

2. Create a `.env` file in the root directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DEEPGRAM_API_KEY=your_deepgram_api_key
   SECRET_KEY=your_secret_key
   ```

3. Build the Docker images:
   ```
   docker-compose build
   ```

4. Start the services:
   ```
   docker-compose up
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Auth & Paywall Service: http://localhost:8080

## Features

The Language Tutor application offers the following features:

- AI-powered conversations for language practice
- Text-based chat interface
- Voice recording and playback for pronunciation practice
- "Torture" button for immediate voice recording and playback
  - This feature allows users to quickly record their voice and immediately play it back, helping them focus on and improve their pronunciation

## Services

The application consists of the following services:

- Backend: FastAPI application
- Frontend: SvelteKit application
- Database: PostgreSQL
- Auth & Paywall: External authentication and subscription service

## Development

The docker-compose setup includes volume mounts for both the backend and frontend, enabling hot-reloading during development.

To run the services individually for development outside of Docker:

- Backend:
  ```
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  ```

- Frontend:
  ```
  cd frontend
  npm install
  npm run dev
  ```

## Testing

To run the tests:

```
docker-compose run backend pytest
```

## Troubleshooting

If you encounter any issues, try the following:

1. Ensure all required environment variables are set in the `.env` file.
2. Rebuild the Docker images: `docker-compose build`
3. Remove existing containers and volumes: `docker-compose down -v`

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
