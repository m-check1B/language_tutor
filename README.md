# Language Tutor Project

[Add a brief description of the Language Tutor project here]

## Authentication and Paywall

This project uses a centralized authentication and paywall system that is embedded within the application. The system is integrated using iframes and postMessage communication on the frontend, and a middleware-based approach on the backend.

### Integration Details

#### Frontend
- The auth and paywall pages are embedded using iframes in the main layout (`src/routes/+layout.svelte`).
- Communication between the Language Tutor app and the auth system is handled via the postMessage API.
- The auth system sends messages for successful login and logout events.
- The Language Tutor app listens for these messages and updates its state accordingly.

#### Backend
- Custom middleware has been implemented to handle authentication and subscription checks.
- All API endpoints that require authentication now use this middleware.
- The authentication flow now uses the external auth_and_paywall system for user management and token validation.
- Subscription status is checked for protected routes to ensure only subscribed users can access certain features.

For more detailed information on the integration approach, please refer to our [Embedded Authentication Approach](../auth_and_paywall/docs/embedded_auth_approach.md) documentation.

### Configuration

To properly configure the integration:

1. Ensure the correct URL for the auth_and_paywall service is set in the environment variables (AUTH_SERVICE_URL).
2. Update the origin check in the message event listener to match your deployment setup.
3. Set the SECRET_KEY and ALGORITHM in the backend environment variables for JWT token handling.
4. Configure the ACCESS_TOKEN_EXPIRE_MINUTES in the backend settings to match the auth_and_paywall service settings.

## Internationalization (i18n)

The Language Tutor project supports multiple languages using the svelte-i18n library. Currently, the following languages are supported:

- English (EN)
- Czech (CS)
- Spanish (ES)

Translation files are located in `src/lib/i18n/` directory. To add or modify translations, edit the corresponding JSON files.

The language is automatically detected based on the URL path (e.g., `/en/`, `/cs/`, `/es/`). Users can switch between languages using the LanguageSwitcher component.

## Getting Started

[Add instructions on how to set up and run the Language Tutor project]

## API Endpoints

The following API endpoints now require authentication and an active subscription:

- POST /conversation/conversations
- GET /conversation/conversations
- POST /conversation/conversations/{conversation_id}/messages
- POST /conversation/conversations/{conversation_id}/transcribe
- GET /conversation/conversations/{conversation_id}/messages

Please ensure you have a valid authentication token and an active subscription when accessing these endpoints.

## Development

When working on features that interact with the authentication or paywall system, be sure to test the integration thoroughly. Pay special attention to:

- The login and logout flows
- Handling of authentication tokens
- Proper display and hiding of auth and subscription management iframes
- API responses for authenticated and unauthenticated requests
- Subscription status checks and corresponding API behaviors
- Correct translation of all user-facing strings
- Proper language switching and URL updating

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

[Add license information here]
