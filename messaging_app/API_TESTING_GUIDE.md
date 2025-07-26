# API Testing Guide

This guide provides comprehensive testing instructions for the Messaging App API using Postman.

## Prerequisites

1. **Start the Django development server:**
   ```bash
   cd messaging_app
   python manage.py runserver
   ```

2. **Create test users:** First, create some test users via Django admin or shell:
   ```bash
   python manage.py shell
   ```
   ```python
   from chats.models import User
   
   # Create test users
   user1 = User.objects.create_user(username='testuser1', email='test1@example.com', password='testpass123')
   user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
   user3 = User.objects.create_user(username='testuser3', email='test3@example.com', password='testpass123')
   
   print(f"User1 ID: {user1.user_id}")
   print(f"User2 ID: {user2.user_id}")
   print(f"User3 ID: {user3.user_id}")
   ```

## Postman Collection Setup

1. Import the `post_man-Collections.json` file into Postman
2. Set up environment variables in Postman:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (will be populated after authentication)
   - `refresh_token`: (will be populated after authentication)
   - `user_id`, `user2_id`, `user3_id`: (User IDs from step 2 above)

## Testing Workflow

### Phase 1: Authentication Testing

#### 1.1 Obtain JWT Token
- **Endpoint:** `POST /api/token/`
- **Purpose:** Get access and refresh tokens
- **Test:** Use `testuser1` credentials
- **Expected:** 200 OK with `access` and `refresh` tokens
- **Action:** Copy tokens to environment variables

#### 1.2 Verify Token
- **Endpoint:** `POST /api/token/verify/`
- **Purpose:** Verify token validity
- **Expected:** 200 OK if token is valid

#### 1.3 Refresh Token
- **Endpoint:** `POST /api/token/refresh/`
- **Purpose:** Get new access token using refresh token
- **Expected:** 200 OK with new access token

### Phase 2: Authorization Testing

#### 2.1 Test Unauthorized Access
- **Endpoints:** Various without Authorization header
- **Expected:** 401 Unauthorized
- **Purpose:** Verify permissions are working

#### 2.2 Test Authenticated Access
- **Endpoints:** Same endpoints with valid token
- **Expected:** 200 OK or appropriate success status
- **Purpose:** Verify authentication works

### Phase 3: Core Functionality Testing

#### 3.1 User Operations
- **List Users:** `GET /api/users/`
- **Get Current User:** `GET /api/users/me/`
- **Search Users:** `GET /api/users/search/?q=testuser`

#### 3.2 Conversation Operations
- **Create Conversation:** `POST /api/conversations/`
  ```json
  {
    "participants": ["<user2_id>", "<user3_id>"]
  }
  ```
- **List Conversations:** `GET /api/conversations/`
- **Get Conversation Details:** `GET /api/conversations/<conversation_id>/`

#### 3.3 Message Operations
- **Send Message:** `POST /api/messages/`
  ```json
  {
    "conversation": "<conversation_id>",
    "message_body": "Hello! This is a test message."
  }
  ```
- **List Messages:** `GET /api/messages/`
- **Update Message:** `PUT /api/messages/<message_id>/`
- **Delete Message:** `DELETE /api/messages/<message_id>/`

### Phase 4: Advanced Features Testing

#### 4.1 Pagination Testing
- **Test:** `GET /api/messages/?page=1`
- **Verify:** Response includes pagination metadata:
  ```json
  {
    "count": 25,
    "next": "http://localhost:8000/api/messages/?page=2",
    "previous": null,
    "results": [...]
  }
  ```

#### 4.2 Filtering Testing

**Filter by Sender:**
- `GET /api/messages/?sender=<user_id>`

**Filter by Username:**
- `GET /api/messages/?sender_username=testuser2`

**Filter by Content:**
- `GET /api/messages/?message_body=hello`

**Filter by Time Range:**
- `GET /api/messages/?sent_after=2025-07-25T00:00:00Z&sent_before=2025-07-26T23:59:59Z`

**Filter Conversations by Participant:**
- `GET /api/conversations/?participant=testuser2`

### Phase 5: Permission Testing

#### 5.1 Participant-Only Access
1. Create a conversation with `testuser1` and `testuser2`
2. Login as `testuser3` (not a participant)
3. Try to access the conversation
4. **Expected:** 404 Not Found or 403 Forbidden

#### 5.2 Message Permissions
1. Create a message as `testuser1`
2. Login as `testuser2` (participant in conversation)
3. Try to view/update/delete the message
4. **Expected:** Can view, cannot update/delete (only sender can)

#### 5.3 Conversation Management
1. Test adding participants: `POST /api/conversations/<id>/add_participant/`
2. Test removing participants: `POST /api/conversations/<id>/remove_participant/`
3. **Expected:** Only participants can manage other participants

## Test Cases Checklist

### Authentication ✓
- [ ] JWT token generation works
- [ ] Token refresh works
- [ ] Token verification works
- [ ] Unauthorized requests are blocked
- [ ] Authorized requests work with valid tokens

### Permissions ✓
- [ ] Only authenticated users can access API
- [ ] Only conversation participants can view messages
- [ ] Only conversation participants can send messages
- [ ] Only message senders can update/delete their messages
- [ ] Non-participants cannot access private conversations

### Pagination ✓
- [ ] Messages are paginated (20 per page)
- [ ] Pagination metadata is included
- [ ] Navigation between pages works
- [ ] Page size can be customized

### Filtering ✓
- [ ] Filter messages by sender
- [ ] Filter messages by sender username
- [ ] Filter messages by content
- [ ] Filter messages by time range
- [ ] Filter conversations by participant
- [ ] Multiple filters work together

### CRUD Operations ✓
- [ ] Create conversations
- [ ] List conversations
- [ ] Get conversation details
- [ ] Add/remove participants
- [ ] Send messages
- [ ] List messages
- [ ] Update messages
- [ ] Delete messages

## Expected Response Formats

### Authentication Response
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Paginated Messages Response
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/messages/?page=2",
  "previous": null,
  "results": [
    {
      "message_id": "123e4567-e89b-12d3-a456-426614174000",
      "sender": {...},
      "conversation": "123e4567-e89b-12d3-a456-426614174001",
      "message_body": "Hello world!",
      "sent_at": "2025-07-26T10:30:00Z"
    }
  ]
}
```

### Error Response
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Troubleshooting

### Common Issues:
1. **401 Unauthorized:** Check if Authorization header is set correctly
2. **403 Forbidden:** User might not be a participant in the conversation
3. **404 Not Found:** Conversation/message might not exist or user has no access
4. **400 Bad Request:** Check request body format and required fields

### Debug Tips:
1. Check Django server logs for detailed error messages
2. Verify user IDs and conversation IDs are correct UUIDs
3. Ensure JWT tokens haven't expired (30-minute lifetime)
4. Check if test data exists in the database
