# Language Tutor Application

This is a multilanguage SvelteKit application that functions as a language tutor. It uses Google Auth for authentication, PostgreSQL as the database, and LiveKit for voice and speech recognition. The application is containerized using Docker for easy deployment.

## Production Setup

Follow these steps to set up and run the application in a production environment:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/language_tutor.git
   cd language_tutor
   ```

2. Set up environment variables:
   - Copy the `.env.template` file to `.env`:
     ```
     cp .env.template .env
     ```
   - Open the `.env` file and fill in all the required values.

3. Build and start the Docker containers:
   ```
   docker-compose up -d --build
   ```

4. Your application should now be running. The services will be available on the following ports:
   - Frontend: 3081
   - Backend: 8081
   - LiveKit: 7880, 7881, 7882 (UDP)

Note: This setup assumes that SSL termination and reverse proxy are handled by the server hosting this VM. Ensure that your server's Nginx (or other proxy) is configured to forward requests to the appropriate ports.

## Maintenance

- To view logs:
  ```
  docker-compose logs
  ```

- To stop the application:
  ```
  docker-compose down
  ```

- To update the application:
  ```
  git pull
  docker-compose up -d --build
  ```

## Troubleshooting

If you encounter any issues:
1. Check the logs of individual services:
   ```
   docker-compose logs [service_name]
   ```
   Replace [service_name] with db, backend, frontend, or livekit.

2. Ensure all environment variables in the `.env` file are correctly set.

3. If changes to the application are not reflecting, try rebuilding the containers:
   ```
   docker-compose up -d --build
   ```

For more detailed troubleshooting, refer to the TROUBLESHOOTING.md file.

## Security Notes

- Keep your `.env` file secure and never commit it to version control.
- Regularly update your dependencies and Docker images to patch any security vulnerabilities.
- Monitor your application logs for any suspicious activities.
- Ensure that the server hosting this VM has proper security measures in place, including firewall rules and regular security updates.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
