#!/bin/bash

# Test script for Docker setup

echo "Testing Docker setup..."

# Build and start the Docker containers
echo "Building and starting Docker containers..."
docker-compose down
docker-compose build
docker-compose up -d

# Wait for the containers to start
echo "Waiting for containers to start..."
sleep 30

# Test the API
echo "Testing the API..."
./test_api.sh

# Check the database
echo "Checking the database..."
docker-compose exec server python check_db.py

# Clean up
echo "Cleaning up..."
docker-compose logs server > server_logs.txt
echo "Server logs saved to server_logs.txt"

echo "Test completed."