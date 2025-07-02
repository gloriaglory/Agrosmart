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
REGISTER_RESPONSE=$(curl -s -X POST \
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

# Extract token from response
AUTH_TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Auth Token: $AUTH_TOKEN"

# If registration fails (user might already exist), try logging in
if [ -z "$AUTH_TOKEN" ]; then
  print_header "Logging in as test user"
  LOGIN_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "password": "testpassword123"
    }' \
    ${BASE_URL}/api/auth/login/)

  # Extract token from login response
  AUTH_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
  echo "Auth Token from login: $AUTH_TOKEN"
fi

# Test the recommend endpoint
print_header "Testing /api/recommend/ endpoint"
RECOMMEND_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -d '{"address": "Nairobi, Kenya"}' \
  ${BASE_URL}/api/recommend/)

# Extract CSRF token from response
CSRF_TOKEN=$(echo $RECOMMEND_RESPONSE | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4)
echo "CSRF Token: $CSRF_TOKEN"

# Use an existing image file for testing
print_header "Using an existing image file"
IMAGE_FILE="media/images/leaf1.jpg"
echo "Using image file: $IMAGE_FILE"

# Test creating a marketplace item with an image
print_header "Creating a marketplace item with an image"
CREATE_RESPONSE=$(curl -s -X POST \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -H "Authorization: Token $AUTH_TOKEN" \
  -F "name=Test Crop" \
  -F "description=A test crop for API testing" \
  -F "price=100.00" \
  -F "category=CROP" \
  -F "quantity=10" \
  -F "location=Nairobi, Kenya" \
  -F "contact_info=+254123456789" \
  -F "image=@$IMAGE_FILE" \
  ${BASE_URL}/api/marketplace/items/)

echo "Create Response: $CREATE_RESPONSE"

# Extract the item ID from the response
ITEM_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Item ID: $ITEM_ID"

# Test getting the marketplace item
print_header "Getting the marketplace item"
GET_RESPONSE=$(curl -s -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/)

echo "Get Response: $GET_RESPONSE"

# Test getting the marketplace item with from_recommend parameter
print_header "Getting the marketplace item with from_recommend parameter"
GET_RECOMMEND_RESPONSE=$(curl -s -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $AUTH_TOKEN" \
  ${BASE_URL}/api/marketplace/items/${ITEM_ID}/?from_recommend=true)

echo "Get with from_recommend Response: $GET_RECOMMEND_RESPONSE"

# Check if the required fields are present in the response
print_header "Checking required fields"
echo "idealTemperature: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"idealTemperature":"[^"]*"')"
echo "suitability: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"suitability":"[^"]*"')"
echo "seller: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"seller":"[^"]*"')"
echo "phone: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"phone":"[^"]*"')"
echo "date: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"date":"[^"]*"')"
echo "imageUrl: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"imageUrl":"[^"]*"')"
echo "image: $(echo $GET_RECOMMEND_RESPONSE | grep -o '"image":"[^"]*"')"

# No cleanup needed as we're using an existing image file

print_header "Test completed"
