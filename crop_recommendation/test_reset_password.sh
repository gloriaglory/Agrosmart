#!/bin/bash

# Test script for reset password functionality
# This script tests the reset password API endpoints using curl

# Set the base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Reset Password Functionality${NC}"
echo "================================================"

# Test 1: Request Password Reset
echo -e "\n${YELLOW}Test 1: Request Password Reset${NC}"
echo "Sending request to ${BASE_URL}/api/auth/password-reset/request/"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com"}' \
  ${BASE_URL}/api/auth/password-reset/request/)

echo "Response: $RESPONSE"
if [[ $RESPONSE == *"message"* ]]; then
  echo -e "${GREEN}✓ Password reset request successful${NC}"
else
  echo -e "${RED}✗ Password reset request failed${NC}"
fi

# Note: Since we can't automatically get the token from email in this script,
# we'll need to manually test the token verification and password reset steps.
echo -e "\n${YELLOW}Note:${NC} To complete the password reset process:"
echo "1. Check the email sent to testuser@example.com"
echo "2. Extract the token from the reset URL"
echo "3. Use the token to verify and reset the password with the following commands:"

echo -e "\n${YELLOW}To verify the token:${NC}"
echo "curl -X POST \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"token\": \"your_reset_token\"}' \\"
echo "  ${BASE_URL}/api/auth/password-reset/verify/"

echo -e "\n${YELLOW}To reset the password:${NC}"
echo "curl -X POST \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"token\": \"your_reset_token\", \"password\": \"newpassword123\", \"password2\": \"newpassword123\"}' \\"
echo "  ${BASE_URL}/api/auth/password-reset/confirm/"

echo -e "\n${YELLOW}To login with the new password:${NC}"
echo "curl -X POST \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"username\": \"testuser\", \"password\": \"newpassword123\"}' \\"
echo "  ${BASE_URL}/api/auth/login/"

echo -e "\n${YELLOW}Test completed.${NC}"
echo "================================================"