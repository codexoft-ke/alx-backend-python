# Messaging App Serializers Documentation

## Overview
This document describes the serializers implemented for the messaging app, handling the many-to-many relationships between Users, Conversations, and Messages.

## Serializer Classes

### 1. UserSerializer
**Purpose**: Full user serialization for CRUD operations
**Features**:
- Password handling (write-only, encryption)
- User creation and updates
- Email validation
- Role-based access

**Fields**:
- `user_id` (read-only)
- `username`, `email`, `first_name`, `last_name`
- `password` (write-only)
- `phone_number`, `role`
- `created_at` (read-only)
- `is_active`, `is_staff`

### 2. UserSimpleSerializer
**Purpose**: Simplified user data for nested relationships
**Use Case**: Used within conversation participants and message senders

**Fields**:
- `user_id`, `username`, `first_name`, `last_name`, `email`, `role`

### 3. MessageSerializer
**Purpose**: Full message serialization with sender details
**Features**:
- Nested sender information
- Conversation reference
- Timestamp tracking

**Fields**:
- `message_id` (read-only)
- `sender` (nested UserSimpleSerializer)
- `sender_id` (write-only for creation)
- `conversation`, `message_body`
- `sent_at`, `created_at`, `updated_at` (read-only)

### 4. MessageSimpleSerializer
**Purpose**: Simplified message data for nested relationships
**Use Case**: Used within conversation message lists

**Fields**:
- `message_id`, `sender`, `message_body`, `sent_at`

### 5. ConversationSerializer
**Purpose**: Full conversation with participants and messages
**Features**:
- Many-to-many participant handling
- Nested message list
- Last message summary
- Message count

**Fields**:
- `conversation_id` (read-only)
- `participants` (nested UserSimpleSerializer list)
- `participant_ids` (write-only for creation/updates)
- `messages` (nested MessageSimpleSerializer list)
- `last_message` (computed field)
- `message_count` (computed field)
- `created_at`, `updated_at` (read-only)

### 6. ConversationSimpleSerializer
**Purpose**: Simplified conversation data for lists
**Use Case**: Conversation overviews and lists

**Fields**:
- `conversation_id`, `participants`
- `last_message` (summary), `message_count`
- `created_at`, `updated_at`

### 7. ConversationDetailSerializer
**Purpose**: Detailed conversation with full message history
**Features**:
- Complete message thread
- Chronological message ordering
- Full participant details

**Fields**:
- `conversation_id`, `participants`
- `messages` (full chronological list)
- `message_count`
- `created_at`, `updated_at`

### 8. MessageCreateSerializer
**Purpose**: Specialized serializer for creating messages
**Features**:
- Automatic sender assignment from request user
- Conversation participant validation
- Security checks

**Fields**:
- `message_id` (read-only)
- `sender` (auto-assigned from request)
- `conversation`, `message_body`

## Many-to-Many Relationships Handled

### User ↔ Conversation (Participants)
- **Field**: `participants` (ManyToManyField)
- **Serialization**: Uses `UserSimpleSerializer` for nested representation
- **Creation**: Uses `participant_ids` list for adding participants
- **Updates**: Supports participant list updates via `participant_ids`

### Conversation → Messages (One-to-Many)
- **Field**: `messages` (reverse ForeignKey)
- **Serialization**: Uses `MessageSimpleSerializer` for nested representation
- **Ordering**: Messages ordered by `sent_at` (chronological)
- **Computed Fields**: `last_message`, `message_count`

### User → Messages (One-to-Many, Sender)
- **Field**: `sender` (ForeignKey)
- **Serialization**: Uses `UserSimpleSerializer` for nested representation
- **Security**: Validates sender permissions in conversations

## Usage Examples

### Creating a Conversation with Participants
```python
data = {
    'participant_ids': [user1.user_id, user2.user_id]
}
serializer = ConversationSerializer(data=data)
if serializer.is_valid():
    conversation = serializer.save()
```

### Creating a Message
```python
data = {
    'conversation': conversation.conversation_id,
    'message_body': 'Hello everyone!'
}
serializer = MessageCreateSerializer(data=data, context={'request': request})
if serializer.is_valid():
    message = serializer.save()
```

### Retrieving Conversation with Messages
```python
conversation = Conversation.objects.get(conversation_id=conv_id)
serializer = ConversationDetailSerializer(conversation)
data = serializer.data  # Includes participants and all messages
```

## Validation Features

1. **Password Security**: Passwords are write-only and properly hashed
2. **Email Validation**: Required and validated email addresses
3. **Participant Validation**: Ensures message senders are conversation participants
4. **Permission Checks**: Validates user permissions for conversation access
5. **Data Integrity**: Maintains referential integrity across relationships

## Performance Considerations

- Uses `select_related()` and `prefetch_related()` for efficient queries
- Simplified serializers for nested relationships to reduce data transfer
- Computed fields cached where appropriate
- Optimized for API response times
