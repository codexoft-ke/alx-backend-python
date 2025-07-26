# Django Middleware Project - 0x03

## Overview

This project focuses on implementing and understanding Django middleware components in a messaging application. The project explores middleware concepts, custom middleware creation, and real-world use cases such as authentication, logging, rate limiting, and request/response filtering.

## Project Structure

The project follows Django best practices with a modular structure:

```
messaging_app/
├── manage.py
├── messaging_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── chats/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
└── requirements.txt
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

The messaging app provides comprehensive RESTful API endpoints:

### Base URL: `/api/`

#### Conversations
- `GET /api/conversations/` - List user's conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Get conversation details
- `PUT/PATCH /api/conversations/{id}/` - Update conversation
- `DELETE /api/conversations/{id}/` - Delete conversation
- `POST /api/conversations/{id}/add_participant/` - Add participant
- `POST /api/conversations/{id}/remove_participant/` - Remove participant
- `GET /api/conversations/{id}/messages/` - Get conversation messages

#### Messages
- `GET /api/messages/` - List user's messages
- `POST /api/messages/` - Send new message
- `GET /api/messages/{id}/` - Get message details
- `PUT/PATCH /api/messages/{id}/` - Update message
- `DELETE /api/messages/{id}/` - Delete message
- `GET /api/messages/my_messages/` - Get current user's messages
- `POST /api/messages/{id}/mark_as_read/` - Mark message as read

#### Users
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get user details
- `GET /api/users/me/` - Get current user profile
- `GET /api/users/search/?q=query` - Search users

#### Utility
- `GET /api/health/` - Health check endpoint

## API Configuration

The project is configured with Django REST Framework with the following settings:

- **Authentication**: Session and Token authentication
- **Permissions**: Authenticated users only
- **Pagination**: 20 items per page
- **Response Format**: JSON only

## Development

To extend the messaging functionality:

1. Add models to `chats/models.py`
2. Create serializers in `chats/serializers.py`
3. Add views to `chats/views.py`
4. Configure URLs in `chats/urls.py`
5. Include app URLs in main `urls.py`

## Testing

Run tests with:
```bash
python manage.py test
```

## Project Requirements

This project fulfills the following requirements:

- ✅ Django project scaffolding with `django-admin startproject`
- ✅ Django REST Framework installation and configuration
- ✅ Chats app creation with `python manage.py startapp chats`
- ✅ Proper project structure and organization
- ✅ Requirements.txt for dependency management
- ✅ Initial database setup with migrations
