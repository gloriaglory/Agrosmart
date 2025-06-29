#!/bin/bash

# Set the base URL
BASE_URL="http://localhost:8000"

# Function to print section headers
print_header() {
  echo -e "\n\033[1;34m$1\033[0m"
  echo "--------------------------------------"
}

# Create a test user directly in the database
print_header "Creating a test user directly in the database"
docker-compose exec -T db psql -U agrosmart -d crop_recommendation -c "
INSERT INTO auth_user (username, email, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES ('testuser', 'test@example.com', 'pbkdf2_sha256\$260000\$q8SA5wFYQiYBVwNQ\$HY1Rw/sZ/1UfUQZRrXGBYdtGJ+HqhZ8YlOPGUMqp3yE=', false, false, true, NOW(), 'Test', 'User')
ON CONFLICT (username) DO NOTHING;
"

# Create a token for the test user
print_header "Creating a token for the test user"
docker-compose exec -T db psql -U agrosmart -d crop_recommendation -c "
INSERT INTO authtoken_token (key, user_id, created)
SELECT 'testtoken123456789', id, NOW()
FROM auth_user
WHERE username = 'testuser'
ON CONFLICT (user_id) DO UPDATE SET key = 'testtoken123456789';
"

# Set the auth token
AUTH_TOKEN="testtoken123456789"
echo "Auth Token: $AUTH_TOKEN"

# Test creating a marketplace item
print_header "Creating a marketplace item"
CREATE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
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

# Test getting the marketplace item with from_recommend parameter
print_header "Getting the marketplace item with from_recommend parameter"
GET_RECOMMEND_RESPONSE=$(curl -s -X GET \
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