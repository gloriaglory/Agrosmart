#!/bin/bash

# Test script for user endpoint
# This script tests the user endpoint by creating a user, logging in, and then accessing the user endpoint

echo "Testing user endpoint..."

# Set the base URL
BASE_URL="http://localhost:8000"

# Create a user
echo "Creating a user..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword123",
    "password2": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
  }')

echo "Register response: $REGISTER_RESPONSE"

# Login with the user
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract the token from the login response
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# Access the user endpoint
echo "Accessing user endpoint..."
USER_RESPONSE=$(curl -s -X GET $BASE_URL/api/auth/user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN")

echo "User response: $USER_RESPONSE"

# Access the profile endpoint
echo "Accessing profile endpoint..."
PROFILE_RESPONSE=$(curl -s -X GET $BASE_URL/api/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN")

echo "Profile response: $PROFILE_RESPONSE"

echo "Test completed."