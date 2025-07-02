#!/bin/bash
# Script to fix Docker setup issues and ensure migrations run properly

# Step 1: Rebuild the container with correct permissions
echo "Stopping current containers..."
docker-compose down || docker stop crop_recommendation-server-1 crop_recommendation-db-1
docker rm crop_recommendation-server-1 crop_recommendation-db-1

# Step 2: Fix migration files
echo "Fixing migration conflicts..."
# Create a merged migration manually if necessary
cat > market_place/migrations/0007_merge_20250701_merged.py << 'EOF'
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('market_place', '0003_marketplaceitem_image'),
        ('market_place', '0006_add_purchase_model'),
    ]

    operations = [
    ]
EOF

# Ensure proper permissions
chmod -R 777 market_place/migrations

# Step 3: Modify Dockerfile to ensure migrations run with correct permissions
echo "Creating Docker migration fix..."
cat > docker_migration_fix.sh << 'EOF'
#!/bin/bash
# This script runs inside the Docker container to handle migrations

set -e

# Create missing migrations directory with correct permissions
mkdir -p /app/market_place/migrations
chmod -R 777 /app/market_place/migrations

# Run Django migrations
python manage.py makemigrations --merge --noinput
python manage.py migrate --noinput

# Initialize the database with basic required tables
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Create missing auth tables
cursor.execute('CREATE TABLE IF NOT EXISTS django_session (session_key VARCHAR(40) NOT NULL PRIMARY KEY, session_data TEXT NOT NULL, expire_date TIMESTAMP WITH TIME ZONE NOT NULL)')
cursor.execute('CREATE TABLE IF NOT EXISTS django_site (id SERIAL PRIMARY KEY, domain VARCHAR(100) NOT NULL, name VARCHAR(50) NOT NULL)')
cursor.execute('INSERT INTO django_site (id, domain, name) VALUES (1, \"example.com\", \"example\") ON CONFLICT DO NOTHING')

# Create authentication user table with phone_number field
cursor.execute('CREATE TABLE IF NOT EXISTS authentication_user (id SERIAL PRIMARY KEY, password VARCHAR(128) NOT NULL, last_login TIMESTAMP WITH TIME ZONE NULL, is_superuser BOOLEAN NOT NULL, username VARCHAR(150) NOT NULL UNIQUE, email VARCHAR(254) NOT NULL, is_staff BOOLEAN NOT NULL, is_active BOOLEAN NOT NULL, date_joined TIMESTAMP WITH TIME ZONE NOT NULL, first_name VARCHAR(150) NOT NULL, last_name VARCHAR(150) NOT NULL, phone_number VARCHAR(20) NULL, id_number VARCHAR(50) NULL)')

# Create other required tables
cursor.execute('CREATE TABLE IF NOT EXISTS education_content (id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, type VARCHAR(10) NOT NULL, url_or_text TEXT NOT NULL, thumbnail VARCHAR(100) NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL)')
cursor.execute('CREATE TABLE IF NOT EXISTS education_comment (id SERIAL PRIMARY KEY, text TEXT NOT NULL, parent_id INTEGER NULL REFERENCES education_comment(id) ON DELETE CASCADE, content_id INTEGER NOT NULL REFERENCES education_content(id) ON DELETE CASCADE, created_at TIMESTAMP WITH TIME ZONE NOT NULL)')
cursor.execute('CREATE TABLE IF NOT EXISTS authtoken_token (key VARCHAR(40) NOT NULL PRIMARY KEY, created TIMESTAMP WITH TIME ZONE NOT NULL, user_id INTEGER NOT NULL UNIQUE)')
"

# Start the application
python manage.py collectstatic --noinput
gunicorn crop_recommendation.wsgi --bind=0.0.0.0:8000 --timeout 120 --workers 4
EOF

chmod +x docker_migration_fix.sh

# Step 4: Create a Dockerfile override to use our fix
cat > Dockerfile.override << 'EOF'
FROM crop_recommendation-server

# Copy our migration fix script
COPY docker_migration_fix.sh /app/docker_migration_fix.sh
RUN chmod +x /app/docker_migration_fix.sh

# Make directories writable
RUN mkdir -p /app/market_place/migrations && \
    chmod -R 777 /app/market_place/migrations

# Override the CMD
CMD ["/app/docker_migration_fix.sh"]
EOF

echo "To rebuild and restart the Docker containers, run:"
echo "docker-compose build --no-cache"
echo "docker-compose up -d"
echo ""
echo "Fix script created. You may need to modify it based on your specific docker-compose setup."
