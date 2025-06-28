-- Initialize the database for Agrosmart application
-- This script will be executed when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist
-- Note: This is usually handled by the POSTGRES_DB environment variable in docker-compose.yml

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a superuser for Django
-- Note: This is usually handled by the environment variables in docker-compose.yml
-- But we can add additional setup here if needed

-- Create tables
-- Note: Django will create tables through migrations, but we can add initial data here

-- Add any initial data needed for testing
-- For example, we could add a test user:
/*
INSERT INTO authentication_user (
    password, 
    last_login, 
    is_superuser, 
    username, 
    first_name, 
    last_name, 
    email, 
    is_staff, 
    is_active, 
    date_joined, 
    phone_number, 
    id_number
) VALUES (
    'pbkdf2_sha256$600000$5py5KZ9rGVgYgVKZN8ZKNM$+XD/0b+5+g5+5py5KZ9rGVgYgVKZN8ZKNM=', -- hashed password for 'password123'
    NULL, 
    FALSE, 
    'testuser', 
    'Test', 
    'User', 
    'testuser@example.com', 
    FALSE, 
    TRUE, 
    NOW(), 
    '+1234567890', 
    'ID12345'
) ON CONFLICT (username) DO NOTHING;
*/

-- Note: The above is commented out because Django will handle user creation
-- and password hashing. This is just an example of what could be done.