# Messaging App API Documentation

## Overview
This document describes the RESTful API endpoints for the messaging application, built with Django REST Framework.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Most endpoints require authentication. Use Django's built-in authentication system.

## API Endpoints

### 1. Conversations API

#### ConversationViewSet
**Base URL**: `/api/conversations/`

##### List Conversations
- **GET** `/api/conversations/`
- **Description**: Get all conversations where the user is a participant
- **Authentication**: Required
- **Query Parameters**:
  - `search`: Search by participant username/email
  - `ordering`: Order by `created_at`, `updated_at` (prefix with `-` for descending)
- **Response**: List of conversations with simplified format

##### Create Conversation
- **POST** `/api/conversations/`
- **Description**: Create a new conversation
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "participant_ids": ["uuid1", "uuid2"]
  }
  ```
- **Response**: Created conversation with detailed format

##### Get Conversation Details
- **GET** `/api/conversations/{conversation_id}/`
- **Description**: Get detailed conversation with all messages
- **Authentication**: Required
- **Response**: Conversation with full message history

##### Update Conversation
- **PUT/PATCH** `/api/conversations/{conversation_id}/`
- **Description**: Update conversation participants
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "participant_ids": ["uuid1", "uuid2", "uuid3"]
  }
  ```

##### Delete Conversation
- **DELETE** `/api/conversations/{conversation_id}/`
- **Description**: Delete a conversation
- **Authentication**: Required

##### Add Participant
- **POST** `/api/conversations/{conversation_id}/add_participant/`
- **Description**: Add a user to the conversation
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_id": "uuid"
  }
  ```

##### Remove Participant
- **POST** `/api/conversations/{conversation_id}/remove_participant/`
- **Description**: Remove a user from the conversation
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_id": "uuid"
  }
  ```

##### Get Conversation Messages
- **GET** `/api/conversations/{conversation_id}/messages/`
- **Description**: Get all messages in a conversation
- **Authentication**: Required
- **Response**: List of messages ordered by sent_at

### 2. Messages API

#### MessageViewSet
**Base URL**: `/api/messages/`

##### List Messages
- **GET** `/api/messages/`
- **Description**: Get all messages from conversations where user is a participant
- **Authentication**: Required
- **Query Parameters**:
  - `conversation`: Filter by conversation ID
  - `sender`: Filter by sender ID
  - `search`: Search in message body or sender username
  - `ordering`: Order by `sent_at`, `created_at` (prefix with `-` for descending)
- **Response**: List of messages with simplified format

##### Send Message
- **POST** `/api/messages/`
- **Description**: Send a new message
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "conversation": "conversation_uuid",
    "message_body": "Your message content"
  }
  ```
- **Response**: Created message details

##### Get Message Details
- **GET** `/api/messages/{message_id}/`
- **Description**: Get detailed message information
- **Authentication**: Required
- **Response**: Message with full details

##### Update Message
- **PUT/PATCH** `/api/messages/{message_id}/`
- **Description**: Update message content
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "message_body": "Updated message content"
  }
  ```

##### Delete Message
- **DELETE** `/api/messages/{message_id}/`
- **Description**: Delete a message
- **Authentication**: Required

##### Get My Messages
- **GET** `/api/messages/my_messages/`
- **Description**: Get all messages sent by the current user
- **Authentication**: Required
- **Response**: List of user's messages

##### Mark Message as Read
- **POST** `/api/messages/{message_id}/mark_as_read/`
- **Description**: Mark a message as read (placeholder)
- **Authentication**: Required

### 3. Users API

#### UserViewSet
**Base URL**: `/api/users/`

##### List Users
- **GET** `/api/users/`
- **Description**: Get list of all users
- **Authentication**: Required
- **Query Parameters**:
  - `search`: Search by username, email, first_name, last_name
  - `ordering`: Order by `username`, `created_at` (prefix with `-` for descending)
- **Response**: List of users

##### Get User Details
- **GET** `/api/users/{user_id}/`
- **Description**: Get detailed user information
- **Authentication**: Required
- **Response**: User details

##### Get Current User
- **GET** `/api/users/me/`
- **Description**: Get current user profile
- **Authentication**: Required
- **Response**: Current user details

##### Search Users
- **GET** `/api/users/search/?q={query}`
- **Description**: Search for users
- **Authentication**: Required
- **Query Parameters**:
  - `q`: Search query (minimum 2 characters)
- **Response**: List of matching users (excludes current user)

### 4. Legacy Endpoints

##### Health Check
- **GET** `/api/health/`
- **Description**: Simple health check
- **Authentication**: Not required
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Messaging app API is running!",
    "version": "1.0.0"
  }
  ```

##### Test Serializers
- **GET** `/api/test-serializers/`
- **Description**: Test endpoint for serializer validation
- **Authentication**: Not required

##### Create Conversation (Legacy)
- **POST** `/api/conversations/create/`
- **Description**: Alternative conversation creation endpoint
- **Authentication**: Required

##### Send Message (Legacy)
- **POST** `/api/conversations/{conversation_id}/send-message/`
- **Description**: Alternative message sending endpoint
- **Authentication**: Required

## Response Formats

### Conversation Response
```json
{
  "conversation_id": "uuid",
  "participants": [
    {
      "user_id": "uuid",
      "username": "username",
      "first_name": "First",
      "last_name": "Last",
      "email": "email@example.com",
      "role": "guest"
    }
  ],
  "messages": [
    {
      "message_id": "uuid",
      "sender": {
        "user_id": "uuid",
        "username": "username",
        "first_name": "First",
        "last_name": "Last",
        "email": "email@example.com",
        "role": "guest"
      },
      "message_body": "Message content",
      "sent_at": "2025-07-18T10:30:00Z"
    }
  ],
  "last_message": {
    "message_id": "uuid",
    "message_body": "Last message content",
    "sent_at": "2025-07-18T10:30:00Z",
    "sender": "username"
  },
  "message_count": 5,
  "created_at": "2025-07-18T10:00:00Z",
  "updated_at": "2025-07-18T10:30:00Z"
}
```

### Message Response
```json
{
  "message_id": "uuid",
  "sender": {
    "user_id": "uuid",
    "username": "username",
    "first_name": "First",
    "last_name": "Last",
    "email": "email@example.com",
    "role": "guest"
  },
  "conversation": "conversation_uuid",
  "message_body": "Message content",
  "sent_at": "2025-07-18T10:30:00Z",
  "created_at": "2025-07-18T10:30:00Z",
  "updated_at": "2025-07-18T10:30:00Z"
}
```

### User Response
```json
{
  "user_id": "uuid",
  "username": "username",
  "email": "email@example.com",
  "first_name": "First",
  "last_name": "Last",
  "phone_number": "+1234567890",
  "role": "guest",
  "created_at": "2025-07-18T10:00:00Z",
  "is_active": true,
  "is_staff": false
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error description",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "You are not a participant in this conversation"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

## Usage Examples

### 1. Create a Conversation
```bash
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": ["user-uuid-1", "user-uuid-2"]
  }'
```

### 2. Send a Message
```bash
curl -X POST http://localhost:8000/api/messages/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": "conversation-uuid",
    "message_body": "Hello, how are you?"
  }'
```

### 3. Get Conversations
```bash
curl -X GET http://localhost:8000/api/conversations/ \
  -H "Authorization: Token your-token-here"
```

### 4. Search Users
```bash
curl -X GET "http://localhost:8000/api/users/search/?q=john" \
  -H "Authorization: Token your-token-here"
```

## Filtering and Pagination

### Filtering
- Use query parameters to filter results
- Available filters vary by endpoint (see individual endpoint documentation)

### Pagination
- API uses Django REST Framework's pagination
- Default page size: 20 items
- Use `page` parameter to navigate pages

### Searching
- Use `search` parameter for text-based searches
- Search fields vary by endpoint

### Ordering
- Use `ordering` parameter to sort results
- Prefix with `-` for descending order
- Available ordering fields vary by endpoint
