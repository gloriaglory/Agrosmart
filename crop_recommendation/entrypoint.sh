#!/bin/bash

# Ensure media directories exist with proper permissions
mkdir -p /app/media/marketplace_images
chmod -R 777 /app/media

# Run migrations with root privileges
python /app/ensure_migrations.py

# Run the main command
exec "$@"
