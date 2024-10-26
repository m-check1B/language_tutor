module.exports = {
  apps: [
    {
      name: 'language-tutor-backend',
      cwd: './backend',
      script: 'python',
      args: '-m uvicorn tests.app.main:app --reload --host 0.0.0.0 --port 8000',
      env: {
        POSTGRES_HOST: 'localhost',
        POSTGRES_PORT: '5432',
        POSTGRES_USER: 'postgres',
        POSTGRES_PASSWORD: 'postgres',
        POSTGRES_DB: 'language_tutor',
        SECRET_KEY: 'dev_secret_key_123456789',
        ALGORITHM: 'HS256',
        ACCESS_TOKEN_EXPIRE_MINUTES: '30'
      }
    },
    {
      name: 'language-tutor-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: './frontend',
      env: {
        VITE_API_URL: 'http://localhost:8000'
      }
    }
  ]
};
