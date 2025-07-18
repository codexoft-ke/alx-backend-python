# Messaging App

A Django REST Framework-based messaging application.

## Project Structure

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

## Features

- Django REST Framework integration
- Modular app structure with `chats` app
- Token-based authentication
- JSON API responses
- Pagination support

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
