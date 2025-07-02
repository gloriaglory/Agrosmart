#!/bin/bash

# Test script for API endpoints

echo "Testing API endpoints..."

# Wait for the server to start
echo "Waiting for server to start..."
sleep 10

# Check if the server is running
echo "Checking if server is running..."
if ! curl -s http://localhost:8000/ > /dev/null; then
  echo "Server is not running. Please start the server first."
  exit 1
fi

# Test login endpoint
echo "Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ad1234min"}')

echo "Login response: $LOGIN_RESPONSE"

# Check if login was successful
if [[ $LOGIN_RESPONSE == *"token"* ]]; then
  echo "Login successful!"
  TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
  echo "Token: $TOKEN"
else
  echo "Login failed. Please check the credentials."
fi

# Test another endpoint to verify session is working
echo "Testing another endpoint..."
curl -s -X GET http://localhost:8000/api/auth/user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN"

echo "Test completed."
