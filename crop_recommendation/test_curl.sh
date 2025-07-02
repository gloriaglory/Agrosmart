#!/bin/bash

# Simple curl test for the API

echo "Testing API with curl..."

# Test login endpoint
echo "Testing login endpoint..."
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ad1234min"}'

echo ""
echo "Test completed."