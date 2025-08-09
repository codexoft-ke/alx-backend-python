#!/bin/bash

# Exit on any failure
set -e

# Wait for database to be ready (if using a database)
echo "Waiting for database..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Start the Django development server
echo "Starting Django server..."
exec gunicorn messaging_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
