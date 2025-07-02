# Database Setup Guide

## Overview

This document provides information about the database setup process for the Agrosmart application. It explains how to handle common migration issues and ensure that all required database tables are properly created.

## The Issue

The application was experiencing an error when accessing the `/api/auth/register/` endpoint:

```
django.db.utils.ProgrammingError: relation "django_session" does not exist
```

This error occurred because the database migrations had not been properly applied, resulting in missing tables required by Django's session management system.

## Solution

We've implemented two solutions to address this issue:

1. **Manual Fix**: Run the migrations to create the required tables
2. **Automated Setup**: Use the `setup_database.sh` script to automate the database setup process

### Manual Fix

If you encounter the "relation does not exist" error, you can manually fix it by running:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate
```

If you encounter conflicts with migrations (particularly in the market_place app), you can use:

```bash
# Fake the conflicting migration
python manage.py migrate market_place 0003_marketplaceitem_image --fake

# Then run all migrations
python manage.py migrate
```

### Automated Setup

We've created a `setup_database.sh` script that automates the database setup process. This script:

1. Activates the virtual environment if it exists
2. Attempts to run migrations normally
3. If migrations fail, it fixes common issues like conflicting migrations
4. Verifies that essential tables exist, and creates them if they don't

To use this script:

```bash
# Make it executable (if not already)
chmod +x setup_database.sh

# Run the script
./setup_database.sh
```

## Docker Integration

The Dockerfile has been updated to use the `setup_database.sh` script during container startup. This ensures that the database is properly set up when the Docker container starts.

## Preventing Future Issues

To prevent similar issues in the future:

1. Always run migrations after pulling new code or switching branches
2. Use the `setup_database.sh` script when setting up a new environment
3. Be careful when creating migrations, especially when multiple developers are working on the same models
4. If you encounter migration conflicts, use the `--fake` option to resolve them

## Troubleshooting

If you still encounter database-related issues:

1. Check the database connection settings in `settings.py`
2. Verify that the database user has the necessary permissions
3. Look for conflicting migrations and resolve them using the `--fake` option
4. If all else fails, you can manually create the required tables using SQL commands (see `setup_database.sh` for examples)