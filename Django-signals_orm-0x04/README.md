# Django Signals ORM - User Notification System

This project implements an automatic user notification system using Django signals. When users receive new messages, the system automatically creates notifications through Django's signal framework.

## Project Overview

The project demonstrates the implementation of Django signals to automatically notify users when they receive new messages. It includes:

- **Message Model**: Stores messages between users
- **Notification Model**: Stores notifications for users
- **UserProfile Model**: Extended user information
- **Django Signals**: Automatic notification creation
- **Admin Interface**: Comprehensive management interface
- **Tests**: Complete test coverage

## Features

### 🔔 Automatic Notifications
- Automatically creates notifications when new messages are received
- Generates read receipts when messages are marked as read
- **NEW**: Creates notifications when messages are edited
- Tracks user online/offline status changes

### 📧 Message System
- Users can send messages to each other
- Messages have read/unread status
- **NEW**: Messages can be edited with full history tracking
- **NEW**: Edit status and timestamps are tracked
- Timestamps for all messages
- Admin interface for message management

### � Message History Tracking
- **NEW**: Automatic logging of all message edits using Django signals
- **NEW**: Stores complete edit history with version numbers
- **NEW**: Tracks who made each edit and when
- **NEW**: Admin interface for viewing edit history
- **NEW**: API endpoints for accessing message history

### �👤 User Management
- Extended user profiles with online status
- User profile automatically created when new users register
- Last seen timestamps

### 🛠 Admin Interface
- Comprehensive Django admin interface
- **NEW**: Message edit status indicators and history links
- **NEW**: MessageHistory admin with full edit tracking
- Bulk actions for messages and notifications
- Filtering and searching capabilities
- Visual indicators for read/unread status

## Models

### Message Model
```python
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages')
    receiver = models.ForeignKey(User, related_name='received_messages')
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)  # NEW
    edited_at = models.DateTimeField(null=True, blank=True)  # NEW
```

### MessageHistory Model (NEW)
```python
class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history')
    old_content = models.TextField(max_length=1000)
    edited_by = models.ForeignKey(User, related_name='message_edits')
    edited_at = models.DateTimeField(default=timezone.now)
    version = models.PositiveIntegerField(default=1)
```

### Notification Model
```python
class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications')
    message = models.ForeignKey(Message, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    # Types include: 'new_message', 'message_read', 'message_edited' (NEW), etc.
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
```

### UserProfile Model
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
```

## Django Signals Implementation

### Signal Handlers

1. **log_message_edit** (NEW): Logs message edits using pre_save signal
2. **create_message_notification**: Creates a notification when a new message is sent
3. **message_read_notification**: Creates a read receipt notification when a message is marked as read
4. **create_user_profile**: Automatically creates a user profile when a new user is created
5. **user_status_notification**: Creates notifications when users go online/offline

### Example Signal Handler (NEW)
```python
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    # Only proceed if this is an update (not a new message)
    if instance.pk:
        try:
            # Get the existing message from database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if the content has actually changed
            if old_message.content != instance.content:
                # Store the old content in MessageHistory
                MessageHistory.create_history_entry(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
                
                # Create notification for the receiver about the edit
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    notification_type='message_edited',
                    title=f"Message edited by {instance.sender.username}",
                    description=f"A message from {instance.sender.username} was edited"
                )
        except Message.DoesNotExist:
            pass
```

## Installation and Setup

### 1. Clone the Repository
```bash
cd /workspaces/alx-backend-python/Django-signals_orm-0x04
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run the Server
```bash
python manage.py runserver
```

## Usage

### Testing the Signal System

1. **Access Django Admin**: Go to `http://127.0.0.1:8000/admin/`
2. **Create Users**: Add test users through the admin interface
3. **Send Messages**: Create messages between users
4. **Edit Messages**: Update message content to see edit history
5. **Check Notifications**: Verify that notifications are automatically created
6. **View History**: Check MessageHistory entries in admin

### Running Tests
```bash
python manage.py test messaging
```

### Testing Message Editing (NEW)
```bash
# Run the message editing test command
python manage.py test_message_editing --clear
```

### Example Usage in Django Shell
```python
python manage.py shell

# Create users
from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory

user1 = User.objects.create_user('sender', 'sender@test.com', 'password')
user2 = User.objects.create_user('receiver', 'receiver@test.com', 'password')

# Send a message (this will automatically create a notification)
message = Message.objects.create(
    sender=user1,
    receiver=user2,
    content="Hello! This message will trigger a notification."
)

# Edit the message (this will create history and edit notification)
message.content = "Hello! This is the EDITED message."
message.save()

# Check that history was created
history_entries = MessageHistory.objects.filter(message=message)
print(f"History entries: {history_entries.count()}")

# Check notifications
notifications = Notification.objects.filter(user=user2)
print(f"Notifications created: {notifications.count()}")

# Mark message as read (this will create a read notification for sender)
message.is_read = True
message.save()

# Check sender's notifications
sender_notifications = Notification.objects.filter(user=user1)
print(f"Sender notifications: {sender_notifications.count()}")
```

## File Structure

```
Django-signals_orm-0x04/
├── manage.py
├── requirements.txt
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── messaging/
    ├── __init__.py
    ├── admin.py          # Django admin configuration
    ├── apps.py           # App configuration with signal loading
    ├── models.py         # Message, Notification, UserProfile models
    ├── signals.py        # Signal handlers for automatic notifications
    ├── tests.py          # Comprehensive test suite
    ├── urls.py           # URL patterns
    └── views.py          # Basic views
```

## Key Signal Features

### 1. Automatic Notification Creation
- Every new message automatically creates a notification for the receiver
- No manual intervention required
- Consistent notification format

### 2. Read Receipt System
- When a message is marked as read, the sender gets notified
- Prevents duplicate read notifications
- Tracks message reading behavior

### 3. User Profile Management
- Automatically creates user profiles for new users
- Tracks online/offline status
- Maintains last seen timestamps

### 4. Error Handling
- Signals include error handling and logging
- Graceful degradation if signal handlers fail
- Debug information in console output

## Testing

The project includes comprehensive tests covering:

- **Model Tests**: All model functionality and methods
- **Signal Tests**: All signal handlers and their effects
- **Integration Tests**: End-to-end messaging flows
- **Edge Cases**: Duplicate notifications, multiple messages, etc.

### Test Coverage
- Message model creation and methods
- Notification model functionality
- UserProfile automatic creation
- Signal handler execution
- Complete messaging workflows

## Admin Interface Features

### Message Admin
- List view with sender, receiver, content preview
- Filtering by read status, users, dates
- Bulk actions to mark as read/unread
- Related notification counts

### Notification Admin
- List view with user, type, title, status
- Filtering by type, read status, dates
- Bulk actions for notification management
- Links to related messages and users

### UserProfile Admin
- Online status indicators
- Message and notification counts
- Bulk actions to set online/offline status
- User activity tracking

## Advanced Features

### 1. Notification Types
- `new_message`: New message received
- `message_read`: Message was read
- `user_online`: User came online
- `user_offline`: User went offline

### 2. Signal Optimization
- Prevents duplicate notifications
- Efficient database queries
- Proper signal disconnection in tests

### 3. Extensibility
- Easy to add new notification types
- Modular signal handlers
- Clean separation of concerns

## Best Practices Implemented

1. **Signal Registration**: Proper signal registration in `apps.py`
2. **Error Handling**: Robust error handling in signal handlers
3. **Testing**: Comprehensive test coverage including signal testing
4. **Documentation**: Detailed docstrings and comments
5. **Admin Interface**: User-friendly admin interface
6. **Model Design**: Proper model relationships and constraints

## Contributing

When extending this project:

1. Add new signal handlers in `signals.py`
2. Update tests to cover new functionality
3. Register new models in `admin.py`
4. Update documentation

## License

This project is part of the ALX Backend Python curriculum.
