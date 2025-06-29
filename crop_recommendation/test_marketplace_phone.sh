#!/bin/bash

# Set the base URL
BASE_URL="http://localhost:8000"

# Function to print section headers
print_header() {
  echo -e "\n\033[1;34m$1\033[0m"
  echo "--------------------------------------"
}

# Set the auth token
AUTH_TOKEN="testtoken123456789"
echo "Auth Token: $AUTH_TOKEN"

# Test creating a marketplace item
print_header "Creating a marketplace item"
CREATE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d '{
    "name": "Test Crop for Phone",
    "description": "A test crop for API testing with phone",
    "price": 150.00,
    "category": "CROP",
    "quantity": 15,
    "location": "Nairobi, Kenya",
    "contact_info": "+254123456789"
  }' \
  ${BASE_URL}/api/marketplace/items/)

echo "Create Response: $CREATE_RESPONSE"

# Extract the item ID from the response
ITEM_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Item ID: $ITEM_ID"

# Test getting the marketplace item without from_recommend parameter
print_header "Getting the marketplace item without from_recommend parameter"
GET_RESPONSE=$(curl -s -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/)

echo "Get Response: $GET_RESPONSE"

# Check for phone field in the response
print_header "Checking for phone field in the response"
if echo "$GET_RESPONSE" | grep -q "\"phone\":"; then
  echo "OK: phone field is present"
  PHONE_VALUE=$(echo $GET_RESPONSE | grep -o "\"phone\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')
  echo "Phone value: $PHONE_VALUE"
else
  echo "ERROR: phone field is missing"
fi

# Test getting the marketplace item with from_recommend parameter
print_header "Getting the marketplace item with from_recommend parameter"
GET_RECOMMEND_RESPONSE=$(curl -s -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/?from_recommend=true)

echo "Get with from_recommend Response: $GET_RECOMMEND_RESPONSE"

# Check for phone field in the response
print_header "Checking for phone field in the from_recommend response"
if echo "$GET_RECOMMEND_RESPONSE" | grep -q "\"phone\":"; then
  echo "OK: phone field is present in from_recommend response"
  PHONE_VALUE=$(echo $GET_RECOMMEND_RESPONSE | grep -o "\"phone\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')
  echo "Phone value: $PHONE_VALUE"
else
  echo "ERROR: phone field is missing in from_recommend response"
fi

print_header "Test completed"