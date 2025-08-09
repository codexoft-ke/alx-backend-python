#!/bin/bash

# Exit on any failure
set -e

# Function to wait for MySQL
wait_for_mysql() {
    echo "Waiting for MySQL database to be ready..."
    while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
        echo "MySQL is unavailable - sleeping"
        sleep 2
    done
    echo "MySQL is up - executing command"
}

# Wait for database to be ready
wait_for_mysql

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

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the Django development server
echo "Starting Django server..."
if [ "$DJANGO_ENV" = "development" ]; then
    exec python3 manage.py runserver 0.0.0.0:8000
else
    exec gunicorn messaging_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
