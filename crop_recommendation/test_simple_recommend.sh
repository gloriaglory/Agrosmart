#!/bin/bash

# Test script for simple-recommend API endpoint
# This script tests the simple-recommend API endpoint using curl

# Set the base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Simple Recommend API Endpoint${NC}"
echo "================================================"

# Test 1: Simple Recommend with address
echo -e "\n${YELLOW}Test 1: Simple Recommend with address${NC}"
echo "Sending request to ${BASE_URL}/api/simple-recommend/"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"address": "Nairobi, Kenya"}' \
  ${BASE_URL}/api/simple-recommend/)

echo "Response received. Checking for expected fields..."

# Check if the response contains the expected fields
if [[ $RESPONSE == *"location"* && $RESPONSE == *"soil_properties"* && $RESPONSE == *"weather"* && $RESPONSE == *"recommendations"* ]]; then
  echo -e "${GREEN}✓ Simple recommend with address successful${NC}"
  echo "Response contains all expected fields"
else
  echo -e "${RED}✗ Simple recommend with address failed${NC}"
  echo "Response: $RESPONSE"
fi

# Test 2: Simple Recommend without address (should use default)
echo -e "\n${YELLOW}Test 2: Simple Recommend without address${NC}"
echo "Sending request to ${BASE_URL}/api/simple-recommend/"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  ${BASE_URL}/api/simple-recommend/)

echo "Response received. Checking for expected fields..."

# Check if the response contains the expected fields
if [[ $RESPONSE == *"location"* && $RESPONSE == *"soil_properties"* && $RESPONSE == *"weather"* && $RESPONSE == *"recommendations"* ]]; then
  echo -e "${GREEN}✓ Simple recommend without address successful${NC}"
  echo "Response contains all expected fields"
else
  echo -e "${RED}✗ Simple recommend without address failed${NC}"
  echo "Response: $RESPONSE"
fi

echo -e "\n${YELLOW}Test completed.${NC}"
echo "================================================"