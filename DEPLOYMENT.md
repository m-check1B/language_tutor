# Language Tutor Application Deployment Guide

This guide outlines the steps to deploy the Language Tutor application in a production environment.

## Prerequisites

- A server with Docker and Docker Compose installed
- Domain name pointing to your server's IP address
- SSL certificate for your domain (we'll use Let's Encrypt)
- Python 3.7+ installed on your local machine for running the production test script

## Deployment Steps

1. **Clone the Repository**

   ```
   git clone https://github.com/your-repo/language-tutor.git
   cd language-tutor
   ```

2. **Set Environment Variables**

   Create a `.env` file in the project root and add the following variables:

   ```
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_api_key
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

3. **Build and Start the Services**

   ```
   docker-compose up -d --build
   ```

4. **Set Up SSL with Let's Encrypt**

   Install Certbot and obtain an SSL certificate:

   ```
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

   Follow the prompts to complete the SSL setup.

5. **Update Nginx Configuration**

   Edit the `nginx.conf` file to include the SSL configuration provided by Certbot. The file should look similar to this:

   ```nginx
   events {
       worker_connections 1024;
   }

   http {
       upstream backend {
           server backend:8000;
       }

       upstream frontend {
           server frontend:3000;
       }

       server {
           listen 80;
           server_name yourdomain.com;
           return 301 https://$server_name$request_uri;
       }

       server {
           listen 443 ssl;
           server_name yourdomain.com;

           ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
           ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

           location / {
               proxy_pass http://frontend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

           location /api {
               proxy_pass http://backend;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

           location /ws {
               proxy_pass http://backend;
               proxy_http_version 1.1;
               proxy_set_header Upgrade $http_upgrade;
               proxy_set_header Connection "upgrade";
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }
       }
   }
   ```

6. **Restart Nginx**

   ```
   docker-compose restart nginx
   ```

7. **Set Up Automatic Renewal for SSL Certificate**

   Create a cron job to automatically renew the SSL certificate:

   ```
   sudo crontab -e
   ```

   Add the following line:

   ```
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

   This will attempt to renew the certificate every day at noon.

8. **Run Production Tests**

   After deployment, run the production test script to ensure everything is working correctly:

   ```
   pip install requests websocket-client
   python production_test.py
   ```

   Make sure to update the `BASE_URL` and `WS_URL` in the `production_test.py` file with your actual domain before running the script.

   If all tests pass, you should see the message "All production tests passed successfully!". If any test fails, review the error message and fix the issue before proceeding.

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

  Replace `service_name` with `backend`, `frontend`, `db`, or `nginx`.

- **Backing Up the Database**

  To create a backup of the PostgreSQL database:

  ```
  docker-compose exec db pg_dump -U postgres language_tutor > backup.sql
  ```

- **Restoring the Database**

  To restore from a backup:

  ```
  cat backup.sql | docker-compose exec -T db psql -U postgres language_tutor
  ```

## Troubleshooting

- If you encounter issues with the WebSocket connection, ensure that your server's firewall allows WebSocket traffic (usually on port 80 or 443).
- If the frontend is not updating after deployment, you may need to clear the browser cache or perform a hard refresh.
- For any persistent issues, check the logs of the relevant service using the `docker-compose logs` command mentioned above.
- If the production tests fail, review the error messages carefully. They should provide information about which part of the application is not functioning as expected.

Remember to regularly update your dependencies and apply security patches to keep your deployment secure.
