#!/bin/bash

# Set the base URL
BASE_URL="http://localhost:8000"

# Function to print section headers
print_header() {
  echo -e "\n\033[1;34m$1\033[0m"
  echo "--------------------------------------"
}

# Register a test user
print_header "Registering a test user"
REGISTER_RESPONSE=$(curl -v -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "password2": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890",
    "id_number": "ID12345"
  }' \
  ${BASE_URL}/api/auth/register/)

echo "Register Response: $REGISTER_RESPONSE"

# Extract token from response
AUTH_TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Auth Token: $AUTH_TOKEN"

# If registration fails (user might already exist), try logging in
if [ -z "$AUTH_TOKEN" ]; then
  print_header "Logging in as test user"
  LOGIN_RESPONSE=$(curl -v -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "password": "testpassword123"
    }' \
    ${BASE_URL}/api/auth/login/)

  echo "Login Response: $LOGIN_RESPONSE"

  # Extract token from login response
  AUTH_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
  echo "Auth Token from login: $AUTH_TOKEN"
fi

# Test the recommend endpoint
print_header "Testing /api/recommend/ endpoint"
RECOMMEND_RESPONSE=$(curl -v -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d '{"address": "Nairobi, Kenya"}' \
  ${BASE_URL}/api/recommend/)

echo "Recommend Response: $RECOMMEND_RESPONSE"

# Extract CSRF token from response
CSRF_TOKEN=$(echo $RECOMMEND_RESPONSE | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4)
echo "CSRF Token: $CSRF_TOKEN"

# Test creating a marketplace item
print_header "Creating a marketplace item"
CREATE_RESPONSE=$(curl -v -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d '{
    "name": "Test Crop",
    "description": "A test crop for API testing",
    "price": 100.00,
    "category": "CROP",
    "quantity": 10,
    "location": "Nairobi, Kenya",
    "contact_info": "+254123456789"
  }' \
  ${BASE_URL}/api/marketplace/items/)

echo "Create Response: $CREATE_RESPONSE"

# Extract the item ID from the response
ITEM_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Item ID: $ITEM_ID"

# Test getting the marketplace item
print_header "Getting the marketplace item"
GET_RESPONSE=$(curl -v -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/)

echo "Get Response: $GET_RESPONSE"

# Test getting the marketplace item with from_recommend parameter
print_header "Getting the marketplace item with from_recommend parameter"
GET_RECOMMEND_RESPONSE=$(curl -v -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/?from_recommend=true)

echo "Get with from_recommend Response: $GET_RECOMMEND_RESPONSE"

# Check for null values in the required fields
print_header "Checking for null values in required fields"

# Function to check if a field has a null value
check_null_value() {
  local field=$1
  local response=$2
  
  # Check if the field exists and is not null
  if echo "$response" | grep -q "\"$field\":null"; then
    echo "ERROR: $field is null"
    return 1
  elif ! echo "$response" | grep -q "\"$field\":"; then
    echo "ERROR: $field is missing"
    return 1
  else
    echo "OK: $field is not null"
    return 0
  fi
}

# Check each required field
check_null_value "idealTemperature" "$GET_RECOMMEND_RESPONSE"
check_null_value "suitability" "$GET_RECOMMEND_RESPONSE"
check_null_value "seller" "$GET_RECOMMEND_RESPONSE"
check_null_value "date" "$GET_RECOMMEND_RESPONSE"

# Print the actual values for reference
echo -e "\nActual values:"
echo "idealTemperature: $(echo $GET_RECOMMEND_RESPONSE | grep -o "\"idealTemperature\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')"
echo "suitability: $(echo $GET_RECOMMEND_RESPONSE | grep -o "\"suitability\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')"
echo "seller: $(echo $GET_RECOMMEND_RESPONSE | grep -o "\"seller\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')"
echo "date: $(echo $GET_RECOMMEND_RESPONSE | grep -o "\"date\":\"[^\"]*\"" | cut -d':' -f2 | tr -d '"')"

print_header "Test completed"