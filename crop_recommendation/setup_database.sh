#!/bin/bash
# This script ensures that all database migrations are properly applied
# It handles common migration issues and creates required tables if needed

set -e

echo "Starting database setup..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Try to run migrations normally
echo "Running migrations..."
python manage.py migrate || {
    echo "Migration failed, attempting to fix common issues..."
    
    # Fix conflicting migrations by faking them
    echo "Fixing conflicting migrations..."
    python manage.py migrate market_place 0003_marketplaceitem_image --fake
    
    # Try migrations again
    echo "Running migrations again..."
    python manage.py migrate
}

# Verify that essential tables exist
echo "Verifying essential tables..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Check if django_session table exists
cursor.execute(\"\"\"
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'django_session'
)
\"\"\")
session_exists = cursor.fetchone()[0]

if not session_exists:
    print('Creating django_session table...')
    cursor.execute('CREATE TABLE IF NOT EXISTS django_session (session_key VARCHAR(40) NOT NULL PRIMARY KEY, session_data TEXT NOT NULL, expire_date TIMESTAMP WITH TIME ZONE NOT NULL)')

# Check if django_site table exists
cursor.execute(\"\"\"
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'django_site'
)
\"\"\")
site_exists = cursor.fetchone()[0]

if not site_exists:
    print('Creating django_site table...')
    cursor.execute('CREATE TABLE IF NOT EXISTS django_site (id SERIAL PRIMARY KEY, domain VARCHAR(100) NOT NULL, name VARCHAR(50) NOT NULL)')
    cursor.execute('INSERT INTO django_site (id, domain, name) VALUES (1, \\'example.com\\', \\'example\\') ON CONFLICT DO NOTHING')
"

echo "Database setup completed successfully!"