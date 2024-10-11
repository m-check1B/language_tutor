# Language Tutor Application Deployment Guide

This guide outlines the steps to deploy the Language Tutor application in a production environment.

## Prerequisites

- An internal VM with Docker and Docker Compose installed
- Nginx server configured as a reverse proxy
- Domain name pointing to your Nginx server's IP address

## Deployment Steps

1. **Clone the Repository**

   ```
   git clone https://github.com/your-repo/language-tutor.git
   cd language-tutor
   ```

2. **Set Environment Variables**

   Create a `.env` file in the project root and add the following variables:

   ```
   PRODUCTION_DOMAIN=your-internal-vm-ip-or-hostname
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=language_tutor
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   BACKEND_SECRET_KEY=your_backend_secret_key
   OPENAI_API_KEY=your_openai_api_key
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

3. **Update Docker Compose File**

   Ensure that the `docker-compose.yml` file has the correct port mappings:

   ```yaml
   version: '3.8'
   services:
     frontend:
       # ... other configurations ...
       ports:
         - "3000:3000"
     
     backend:
       # ... other configurations ...
       ports:
         - "8000:8000"
     
     # ... other services ...
   ```

4. **Build and Start the Services**

   ```
   docker-compose up -d --build
   ```

5. **Configure Nginx**

   Update your Nginx configuration to proxy requests to the correct ports:

   ```nginx
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       location /ws {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "Upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

6. **Restart Nginx**

   ```
   sudo systemctl restart nginx
   ```

7. **Run Production Tests**

   ```
   python3 production_test.py
   ```

## Maintenance

- **Updating the Application**

  To update the application with new changes:

  ```
  git pull origin main
  docker-compose up -d --build
  ```

- **Viewing Logs**

  To view logs for a specific service:

  ```
  docker-compose logs -f service_name
  ```

  Replace `service_name` with `frontend`, `backend`, or `db`.

- **Backing Up the Database**

  To create a backup of the PostgreSQL database:

  ```
  docker-compose exec db pg_dump -U your_db_user language_tutor > backup.sql
  ```

- **Restoring the Database**

  To restore from a backup:

  ```
  cat backup.sql | docker-compose exec -T db psql -U your_db_user language_tutor
  ```

## Troubleshooting

- If you encounter issues with the WebSocket connection, ensure that your Nginx configuration is correctly set up to proxy WebSocket connections.
- If the frontend is not updating after deployment, you may need to clear the browser cache or perform a hard refresh.
- For any persistent issues, check the logs of the relevant service using the `docker-compose logs` command mentioned above.

Remember to regularly update your dependencies and apply security patches to keep your deployment secure.

## Note on Internal VM Setup

This application is designed to run on an internal VM behind an Nginx server. The frontend runs on port 3000, and the backend runs on port 8000. This setup should be considered when performing tests, maintenance, or troubleshooting. Ensure that your firewall settings allow traffic on these ports between the Nginx server and the internal VM.
