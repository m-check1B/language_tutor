# Language Tutor API Documentation

## Overview

This document provides detailed information about the API endpoints and WebSocket communication for the Language Tutor application.

## Authentication

All API endpoints and WebSocket connections require authentication using a JWT token. Include the token in the `Authorization` header of your requests:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Start Conversation

Initiates a new conversation session.

- **URL**: `/livekit/start-conversation`
- **Method**: `POST`
- **Auth required**: Yes

#### Success Response

- **Code**: 200 OK
- **Content**: 
  ```json
  {
    "conversation_id": "<conversation_id>"
  }
  ```

#### Error Response

- **Code**: 500 Internal Server Error
- **Content**: 
  ```json
  {
    "detail": "Failed to start conversation"
  }
  ```

### 2. End Conversation

Ends an active conversation session.

- **URL**: `/livekit/end-conversation/{conversation_id}`
- **Method**: `POST`
- **Auth required**: Yes
- **URL Params**: `conversation_id=[string]`

#### Success Response

- **Code**: 200 OK
- **Content**: 
  ```json
  {
    "message": "Conversation ended successfully"
  }
  ```

#### Error Response

- **Code**: 500 Internal Server Error
- **Content**: 
  ```json
  {
    "detail": "Failed to end conversation"
  }
  ```

## WebSocket Communication

### Connection

- **URL**: `ws://localhost:8081/livekit/ws/chat/{conversation_id}`
- **Auth required**: Yes (JWT token should be included in the connection URL)

### Message Format

Messages sent and received through the WebSocket connection should follow this format:

```json
{
  "type": "<message_type>",
  "content": "<message_content>"
}
```

Where `<message_type>` can be either "text" or "audio", and `<message_content>` is the actual message content (text string for text messages, base64-encoded audio data for audio messages).

### Sending Messages

To send a message, send a JSON object with the following structure:

```json
{
  "type": "text",
  "content": "Hello, how are you?"
}
```

or for audio messages:

```json
{
  "type": "audio",
  "content": "<base64_encoded_audio_data>"
}
```

### Receiving Messages

Messages received from the server will have the following structure:

```json
{
  "conversation_id": "<conversation_id>",
  "content": "<response_content>",
  "type": "<response_type>"
}
```

Where `<response_type>` can be either "text" or "audio", and `<response_content>` is the actual response content (text string for text responses, base64-encoded audio data for audio responses).

### Error Messages

If an error occurs during message processing, the server will send an error message with the following structure:

```json
{
  "error": "<error_message>"
}
```

## Error Handling

The application implements the following error handling mechanisms:

1. Invalid message formats or types will result in an error message sent back through the WebSocket.
2. Network disconnections trigger automatic reconnection attempts (up to 5 times with a 5-second interval).
3. LiveKit agent initialization failures and other server-side errors are logged and result in appropriate error responses.

## Best Practices

1. Always check the WebSocket connection status before sending messages.
2. Implement proper error handling on the client side to manage various error scenarios.
3. For audio messages, ensure the audio data is properly encoded to base64 before sending.
4. Keep messages concise to avoid potential issues with message size limits.
