#!/bin/bash

# Test script for Education API endpoints
# This script tests all Education API endpoints using curl from Docker (localhost:8000)

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
echo -e "${BLUE}     EDUCATION API TESTING SCRIPT          ${NC}"
echo -e "${BLUE}============================================${NC}"

# Test variables
USERNAME="testuser"
EMAIL="testuser@example.com"
PASSWORD="securepassword123"
AUTH_TOKEN=""

# ===== Authentication =====
section "Authentication"

# Login to get token
test_header "Login to get token"
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
  echo "Continuing with tests, but authenticated endpoints may fail"
fi

# ===== Education API Tests =====
section "Education API Tests"

# List all content
test_header "List all content"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/education/contents/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == "[]" || $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ List all content successful${NC}"
else
  echo -e "${RED}✗ List all content failed${NC}"
fi

# Create content (requires authentication)
test_header "Create content"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"title\": \"Test Content\", \"type\": \"article\", \"url_or_text\": \"This is a test article content.\"}" \
  ${BASE_URL}/api/education/contents/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ Create content successful${NC}"
  # Extract content ID for future requests
  CONTENT_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | sed 's/"id"://')
  echo "Content ID: $CONTENT_ID"
else
  echo -e "${RED}✗ Create content failed${NC}"
  # Use a default content ID for testing
  CONTENT_ID=1
  echo "Using default content ID: $CONTENT_ID"
fi

# Get specific content
test_header "Get specific content"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/education/contents/$CONTENT_ID/)

check_response "$RESPONSE" "title" "Get specific content"

# Update content (requires authentication)
test_header "Update content"
RESPONSE=$(curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"title\": \"Updated Test Content\"}" \
  ${BASE_URL}/api/education/contents/$CONTENT_ID/)

check_response "$RESPONSE" "title" "Update content"

# List all comments
test_header "List all comments"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/education/comments/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == "[]" || $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ List all comments successful${NC}"
else
  echo -e "${RED}✗ List all comments failed${NC}"
fi

# Create comment (requires authentication)
test_header "Create comment"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"text\": \"This is a test comment.\", \"content\": $CONTENT_ID}" \
  ${BASE_URL}/api/education/comments/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"id"* ]]; then
  echo -e "${GREEN}✓ Create comment successful${NC}"
  # Extract comment ID for future requests
  COMMENT_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | sed 's/"id"://')
  echo "Comment ID: $COMMENT_ID"
else
  echo -e "${RED}✗ Create comment failed${NC}"
  # Use a default comment ID for testing
  COMMENT_ID=1
  echo "Using default comment ID: $COMMENT_ID"
fi

# Get specific comment
test_header "Get specific comment"
RESPONSE=$(curl -s -X GET ${BASE_URL}/api/education/comments/$COMMENT_ID/)

check_response "$RESPONSE" "text" "Get specific comment"

# Update comment (requires authentication)
test_header "Update comment"
RESPONSE=$(curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d "{\"text\": \"This is an updated test comment.\"}" \
  ${BASE_URL}/api/education/comments/$COMMENT_ID/)

check_response "$RESPONSE" "text" "Update comment"

# Delete comment (requires authentication)
test_header "Delete comment"
RESPONSE=$(curl -s -X DELETE \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/education/comments/$COMMENT_ID/)

if [[ -z "$RESPONSE" ]]; then
  echo -e "${GREEN}✓ Delete comment successful${NC}"
else
  echo -e "${RED}✗ Delete comment failed${NC}"
  echo "Response: $RESPONSE"
fi

# Delete content (requires authentication)
test_header "Delete content"
RESPONSE=$(curl -s -X DELETE \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/education/contents/$CONTENT_ID/)

if [[ -z "$RESPONSE" ]]; then
  echo -e "${GREEN}✓ Delete content successful${NC}"
else
  echo -e "${RED}✗ Delete content failed${NC}"
  echo "Response: $RESPONSE"
fi

# ===== Summary =====
section "Test Summary"
echo -e "${GREEN}All tests completed.${NC}"
echo "Note: Some tests may have failed if the server is not running or if the endpoints are not properly configured."
echo "Check the output above for details on which tests passed and which failed."
echo -e "${BLUE}============================================${NC}"