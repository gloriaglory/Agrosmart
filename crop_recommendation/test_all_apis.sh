#!/bin/bash

# Comprehensive test script for all Agrosmart APIs
# This script tests all API endpoints using curl from Docker (localhost:8000)

# Set the base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
  echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to print test headers
test_header() {
  echo -e "\n${YELLOW}Test: $1${NC}"
}

# Function to check response
check_response() {
  local response=$1
  local expected=$2
  local test_name=$3
  
  if [[ $response == *"$expected"* ]]; then
    echo -e "${GREEN}✓ $test_name successful${NC}"
  else
    echo -e "${RED}✗ $test_name failed${NC}"
    echo "Response: $response"
  fi
}

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}     AGROSMART API TESTING SCRIPT          ${NC}"
echo -e "${BLUE}============================================${NC}"

# Test variables
USERNAME="testuser"
EMAIL="testuser@example.com"
PASSWORD="securepassword123"
AUTH_TOKEN=""

# ===== Authentication API Tests =====
section "Authentication API Tests"

# Register a new user
test_header "Register a new user"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"password2\": \"$PASSWORD\", \"first_name\": \"Test\", \"last_name\": \"User\", \"phone_number\": \"+1234567890\"}" \
  ${BASE_URL}/api/auth/register/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"token"* ]]; then
  echo -e "${GREEN}✓ Registration successful${NC}"
  # Extract token for future requests
  AUTH_TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')
  echo "Token: $AUTH_TOKEN"
else
  # If registration fails, it might be because the user already exists
  echo -e "${YELLOW}! Registration failed, attempting login${NC}"
fi

# Login
test_header "Login"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" \
  ${BASE_URL}/api/auth/login/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"token"* ]]; then
  echo -e "${GREEN}✓ Login successful${NC}"
  # Extract token for future requests
  AUTH_TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')
  echo "Token: $AUTH_TOKEN"
else
  echo -e "${RED}✗ Login failed${NC}"
  echo "Continuing with tests, but authenticated endpoints will fail"
fi

# Get user profile
test_header "Get user profile"
RESPONSE=$(curl -s -X GET \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/auth/profile/)

check_response "$RESPONSE" "username" "Get user profile"

# Update user profile
test_header "Update user profile"
RESPONSE=$(curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"first_name\": \"Updated\", \"last_name\": \"User\", \"id_number\": \"ID123456\"}" \
  ${BASE_URL}/api/auth/profile/update/)

check_response "$RESPONSE" "first_name" "Update user profile"

# Request password reset
test_header "Request password reset"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\"}" \
  ${BASE_URL}/api/auth/password-reset/request/)

check_response "$RESPONSE" "message" "Request password reset"

# Note: We can't automatically test token verification and password reset
# as they require a token from email
echo -e "${YELLOW}Note: Token verification and password reset require a token from email${NC}"
echo "To manually test these endpoints, see test_reset_password.sh"

# ===== Crop Recommendation API Tests =====
section "Crop Recommendation API Tests"

# Recommend crop
test_header "Recommend crop"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"Nairobi, Kenya\"}" \
  ${BASE_URL}/api/recommend/)

check_response "$RESPONSE" "recommendations" "Recommend crop"

# Simple recommend crop
test_header "Simple recommend crop"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"Nairobi, Kenya\"}" \
  ${BASE_URL}/api/simple-recommend/)

check_response "$RESPONSE" "recommendations" "Simple recommend crop"

# ===== Marketplace API Tests =====
section "Marketplace API Tests"

# List marketplace items
test_header "List marketplace items"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/marketplace/items/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == "[]" || $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ List marketplace items successful${NC}"
else
  echo -e "${RED}✗ List marketplace items failed${NC}"
fi

# Create marketplace item
test_header "Create marketplace item"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"name\": \"Test Item\", \"description\": \"Test description\", \"price\": \"100.00\", \"category\": \"OTHER\", \"quantity\": 10, \"location\": \"Test Location\", \"contact_info\": \"+1234567890\"}" \
  ${BASE_URL}/api/marketplace/items/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ Create marketplace item successful${NC}"
  # Extract item ID for future requests
  ITEM_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | sed 's/"id"://')
  echo "Item ID: $ITEM_ID"
else
  echo -e "${RED}✗ Create marketplace item failed${NC}"
  # Use a default item ID for testing
  ITEM_ID=1
  echo "Using default item ID: $ITEM_ID"
fi

# Get marketplace item
test_header "Get marketplace item"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/marketplace/items/$ITEM_ID/)

check_response "$RESPONSE" "name" "Get marketplace item"

# Update marketplace item
test_header "Update marketplace item"
RESPONSE=$(curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"price\": \"150.00\", \"quantity\": 5}" \
  ${BASE_URL}/api/marketplace/items/$ITEM_ID/)

check_response "$RESPONSE" "price" "Update marketplace item"

# Delete marketplace item
test_header "Delete marketplace item"
RESPONSE=$(curl -s -X DELETE \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/$ITEM_ID/)

if [[ -z "$RESPONSE" ]]; then
  echo -e "${GREEN}✓ Delete marketplace item successful${NC}"
else
  echo -e "${RED}✗ Delete marketplace item failed${NC}"
  echo "Response: $RESPONSE"
fi

# ===== Summary =====
section "Test Summary"
echo -e "${GREEN}All tests completed.${NC}"
echo "Note: Some tests may have failed if the server is not running or if the endpoints are not properly configured."
echo "Check the output above for details on which tests passed and which failed."
echo -e "${BLUE}============================================${NC}"