# Testing the API Fix

This document explains how to test the fix for the API error related to the missing `django_session` table.

## Overview

The issue was that the API was returning a 500 error when accessing the `/api/auth/login/` endpoint because the `django_session` table did not exist in the database. We've implemented a fix that ensures the table is created properly before the application starts.

## Testing Scripts

We've created several scripts to help test the fix:

1. `ensure_migrations.py`: This script ensures that all necessary database migrations are applied and creates essential tables directly if migrations fail.
2. `test_api.sh`: This script tests the API endpoints to verify that they're working correctly.
3. `check_db.py`: This script checks if essential tables exist in the database.
4. `test_docker.sh`: This script builds and runs the Docker containers, then tests the API and database.
5. `test_curl.sh`: This script provides a simple curl command to test the API directly.

## How to Test

### Option 1: Using Docker

1. Make sure Docker and Docker Compose are installed on your system.
2. Run the test script:
   ```bash
   ./test_docker.sh
   ```
   This script will:
   - Build and start the Docker containers
   - Wait for the containers to start
   - Test the API endpoints
   - Check if essential tables exist in the database
   - Save the server logs for debugging

3. Check the results:
   - If the API tests pass, it means the fix is working correctly.
   - If the database checks show that all essential tables exist, it means the migrations are being applied properly.
   - If there are any issues, check the server logs in `server_logs.txt`.

### Option 2: Manual Testing

If you prefer to test the fix manually, follow these steps:

1. Build and start the Docker containers:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

2. Wait for the containers to start:
   ```bash
   sleep 30
   ```

3. Test the API:
   ```bash
   ./test_api.sh
   ```

4. Check the database:
   ```bash
   docker-compose exec server python check_db.py
   ```

5. Check the server logs:
   ```bash
   docker-compose logs server
   ```

### Option 3: Quick Test with Curl

If you just want to quickly test if the API is working, you can use the `test_curl.sh` script:

1. Make sure the Docker containers are running:
   ```bash
   docker-compose ps
   ```

2. Run the curl test:
   ```bash
   ./test_curl.sh
   ```

   If you see a response with a token, it means the fix is working correctly:
   ```json
   {"key":"your-token-here"}
   ```

   If you see an error, it means there's still an issue with the API.

## What the Fix Does

The fix consists of several components:

1. An `ensure_migrations.py` script that:
   - Tries to run migrations normally
   - Fixes common issues if migrations fail
   - Creates essential tables directly if needed
   - Verifies that essential tables exist

2. Updates to the Dockerfile to:
   - Copy the script before switching to the non-privileged user
   - Make the script executable

3. Updates to the entrypoint.sh script to:
   - Run the script with root privileges before starting the application

These changes ensure that the `django_session` table is created properly before the application starts, which fixes the 500 error when accessing the `/api/auth/login/` endpoint.
