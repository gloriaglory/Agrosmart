# Agrosmart API Documentation

This document provides comprehensive documentation for the Agrosmart API, including detailed information on all endpoints and how to test them using Postman.

## Table of Contents
1. [Overview](#overview)
2. [Setting Up Postman](#setting-up-postman)
3. [Authentication API](#authentication-api)
4. [Crop Recommendation API](#crop-recommendation-api)
5. [Disease Detection API](#disease-detection-api)
6. [Marketplace API](#marketplace-api)
7. [Testing Seller and Buyer Roles](#testing-seller-and-buyer-roles)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)

## Overview

The Agrosmart API provides several services:
- User authentication and profile management
- Crop recommendation based on soil and weather conditions
- Plant disease detection from images
- Agricultural marketplace for buying and selling products

Base URL: `http://localhost:8000` (for local development)

### CSRF Protection

All API endpoints (paths starting with `/api/` or `/detector/`) are exempt from CSRF protection. This means you don't need to include CSRF tokens in your API requests, even for POST, PUT, PATCH, and DELETE methods. This makes it easier to use the API with external clients like Postman or mobile apps.

## Setting Up Postman

### Installation
1. Download and install Postman from [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
2. Create a free account or continue as a guest

### Creating a Collection
1. Open Postman and click "Create Collection"
2. Name it "Agrosmart API"
3. Click the three dots next to the collection name and select "Edit"
4. Go to the "Variables" tab and add the following variables:
   - `base_url`: `http://localhost:8000` (or your server URL)
   - `token`: Leave this empty for now (will be filled after login)

### Setting Up Authentication
1. After logging in, copy the token from the response
2. Click on the collection name
3. Go to the "Variables" tab
4. Paste the token in the "Current Value" field for the `token` variable
5. Click "Save"

Now you can use `{{base_url}}` and `{{token}}` in your requests.

## Authentication API

All authentication endpoints are prefixed with `/api/auth/`.

### Register a New User

**Endpoint:** `POST {{base_url}}/api/auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "your_username",
  "email": "your_email@example.com",
  "password": "your_password",
  "password2": "your_password",
  "first_name": "Your",
  "last_name": "Name",
  "phone_number": "+1234567890",
  "id_number": "ID12345"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name",
    "phone_number": "+1234567890",
    "id_number": "ID12345",
    "role": "seller"
  },
  "token": "your_auth_token"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/auth/register/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter the request body as shown above
5. Click "Send"

### Login

**Endpoint:** `POST {{base_url}}/api/auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name",
    "phone_number": "+1234567890",
    "id_number": "ID12345",
    "role": "seller"
  },
  "token": "your_auth_token"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/auth/login/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter the request body as shown above
5. Click "Send"
6. Copy the token from the response and update the collection variable

### Get Token

**Endpoint:** `POST {{base_url}}/api/auth/token/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200 OK):**
```json
{
  "token": "your_auth_token"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/auth/token/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter the request body as shown above
5. Click "Send"
6. Copy the token from the response and update the collection variable

### Google Login

**Endpoint:** `POST {{base_url}}/api/auth/google/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "access_token": "google_oauth2_access_token"
}
```

**Response (200 OK):**
```json
{
  "key": "your_auth_token"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/auth/google/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter the request body with your Google OAuth2 access token
5. Click "Send"
6. Copy the token from the response and update the collection variable

### Facebook Login

**Endpoint:** `POST {{base_url}}/api/auth/facebook/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "access_token": "facebook_oauth2_access_token"
}
```

**Response (200 OK):**
```json
{
  "key": "your_auth_token"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/auth/facebook/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter the request body with your Facebook OAuth2 access token
5. Click "Send"
6. Copy the token from the response and update the collection variable

### Get User Profile

**Endpoint:** `GET {{base_url}}/api/auth/profile/`

**Headers:**
```
Authorization: Token {{token}}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "Your",
  "last_name": "Name",
  "phone_number": "+1234567890",
  "id_number": "ID12345",
  "role": "seller"
}
```

**Postman Example:**
1. Create a new GET request
2. Enter `{{base_url}}/api/auth/profile/` as the URL
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Click "Send"

### Update User Profile

**Endpoint:** `PUT {{base_url}}/api/auth/profile/update/`

**Headers:**
```
Content-Type: application/json
Authorization: Token {{token}}
```

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "phone_number": "+9876543210",
  "id_number": "ID67890"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "phone_number": "+9876543210",
  "id_number": "ID67890",
  "role": "seller"
}
```

**Postman Example:**
1. Create a new PUT request
2. Enter `{{base_url}}/api/auth/profile/update/` as the URL
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Go to the "Body" tab, select "raw" and "JSON"
6. Enter the request body as shown above
7. Click "Send"

## Crop Recommendation API

### Recommend Crop

**Endpoint:** `POST {{base_url}}/api/recommend/`

**Headers:**
```
Content-Type: application/json
```

**Request Body (Option 1 - Using Address):**
```json
{
  "address": "Nairobi, Kenya"
}
```

**Request Body (Option 2 - Using Coordinates):**
```json
{
  "latitude": -1.2921,
  "longitude": 36.8219
}
```

**Response (200 OK):**
```json
{
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219,
    "address": "Nairobi, Kenya"
  },
  "soil_properties": {
    "Nitrogen Total (0-20cm)": 0.5,
    "Phosphorus Extractable (0-20cm)": 35.2,
    "Potassium Extractable (0-20cm)": 145.8,
    "Soil pH (0-20cm)": 6.2
  },
  "weather": {
    "temperature": 22.5,
    "humidity": 65,
    "rainfall": 800
  },
  "recommendations": {
    "Maize": {
      "explanation": "Maize grows well in warm areas with temperatures between 18-30°C and requires moderate rainfall of 600-1200mm annually. It prefers well-drained soils with a pH of 5.5-7.0 and good levels of nitrogen.",
      "score": 0.85
    },
    "Beans": {
      "explanation": "Beans thrive in temperatures of 18-25°C and require 300-500mm of rainfall per growing season. They prefer well-drained soils with a pH of 6.0-7.5 and can fix nitrogen from the atmosphere.",
      "score": 0.75
    }
  }
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/recommend/` as the URL
3. Go to the "Body" tab, select "raw" and "JSON"
4. Enter one of the request body options shown above
5. Click "Send"

## Disease Detection API

### Detect Plant Disease

**Endpoint:** `POST {{base_url}}/detector/detect`

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
- Form data with key `file` and value as an image file

**Response (200 OK):**
```json
{
  "disease": "Corn Common Rust",
  "confidence": 0.95,
  "description": "Common rust is caused by the fungus Puccinia sorghi. Symptoms include small, round to elongate brown pustules on both leaf surfaces. The pustules contain rust-colored spores that are easily dislodged and can be rubbed off onto fingers or clothing.",
  "treatment": "Apply fungicides containing active ingredients like azoxystrobin, pyraclostrobin, or propiconazole. Rotate crops and plant resistant varieties when available. Remove infected plant debris after harvest."
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/detector/detect` as the URL
3. Go to the "Body" tab, select "form-data"
4. Add a key named `file` and select "File" as the type
5. Click "Select Files" and choose an image of a plant leaf
6. Click "Send"

## Marketplace API

All marketplace endpoints are prefixed with `/api/marketplace/`.

### List All Items

**Endpoint:** `GET {{base_url}}/api/marketplace/items/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Maize Seeds",
    "description": "High-quality maize seeds",
    "price": "500.00",
    "category": "OTHER",
    "quantity": 100,
    "location": "Nairobi",
    "contact_info": "+254700000000",
    "created_at": "2023-08-01T12:00:00Z",
    "updated_at": "2023-08-01T12:00:00Z"
  },
  {
    "id": 2,
    "name": "Organic Fertilizer",
    "description": "Natural organic fertilizer for all crops",
    "price": "1200.00",
    "category": "OTHER",
    "quantity": 50,
    "location": "Mombasa",
    "contact_info": "+254711111111",
    "created_at": "2023-08-02T10:30:00Z",
    "updated_at": "2023-08-02T10:30:00Z"
  }
]
```

**Postman Example:**
1. Create a new GET request
2. Enter `{{base_url}}/api/marketplace/items/` as the URL
3. Click "Send"

### Get Item by ID

**Endpoint:** `GET {{base_url}}/api/marketplace/items/{id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Maize Seeds",
  "description": "High-quality maize seeds",
  "price": "500.00",
  "category": "OTHER",
  "quantity": 100,
  "location": "Nairobi",
  "contact_info": "+254700000000",
  "created_at": "2023-08-01T12:00:00Z",
  "updated_at": "2023-08-01T12:00:00Z"
}
```

**Postman Example:**
1. Create a new GET request
2. Enter `{{base_url}}/api/marketplace/items/1/` as the URL (replace 1 with the actual item ID)
3. Click "Send"

### Create New Item

**Endpoint:** `POST {{base_url}}/api/marketplace/items/`

**Headers:**
```
Content-Type: application/json
Authorization: Token {{token}}
```

**Request Body:**
```json
{
  "name": "Tomato Seedlings",
  "description": "Healthy tomato seedlings ready for transplanting",
  "price": "300.00",
  "category": "OTHER",
  "quantity": 200,
  "location": "Kisumu",
  "contact_info": "+254722222222"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Tomato Seedlings",
  "description": "Healthy tomato seedlings ready for transplanting",
  "price": "300.00",
  "category": "OTHER",
  "quantity": 200,
  "location": "Kisumu",
  "contact_info": "+254722222222",
  "created_at": "2023-08-03T09:15:00Z",
  "updated_at": "2023-08-03T09:15:00Z"
}
```

**Postman Example:**
1. Create a new POST request
2. Enter `{{base_url}}/api/marketplace/items/` as the URL
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Go to the "Body" tab, select "raw" and "JSON"
6. Enter the request body as shown above
7. Click "Send"

### Update Item

**Endpoint:** `PUT {{base_url}}/api/marketplace/items/{id}/`

**Headers:**
```
Content-Type: application/json
Authorization: Token {{token}}
```

**Request Body:**
```json
{
  "name": "Tomato Seedlings",
  "description": "Organic tomato seedlings ready for transplanting",
  "price": "350.00",
  "category": "OTHER",
  "quantity": 150,
  "location": "Kisumu",
  "contact_info": "+254722222222"
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Tomato Seedlings",
  "description": "Organic tomato seedlings ready for transplanting",
  "price": "350.00",
  "category": "OTHER",
  "quantity": 150,
  "location": "Kisumu",
  "contact_info": "+254722222222",
  "created_at": "2023-08-03T09:15:00Z",
  "updated_at": "2023-08-03T10:20:00Z"
}
```

**Postman Example:**
1. Create a new PUT request
2. Enter `{{base_url}}/api/marketplace/items/3/` as the URL (replace 3 with the actual item ID)
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Go to the "Body" tab, select "raw" and "JSON"
6. Enter the request body as shown above
7. Click "Send"

### Partially Update Item

**Endpoint:** `PATCH {{base_url}}/api/marketplace/items/{id}/`

**Headers:**
```
Content-Type: application/json
Authorization: Token {{token}}
```

**Request Body:**
```json
{
  "price": "375.00",
  "quantity": 125
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Tomato Seedlings",
  "description": "Organic tomato seedlings ready for transplanting",
  "price": "375.00",
  "category": "OTHER",
  "quantity": 125,
  "location": "Kisumu",
  "contact_info": "+254722222222",
  "created_at": "2023-08-03T09:15:00Z",
  "updated_at": "2023-08-03T11:30:00Z"
}
```

**Postman Example:**
1. Create a new PATCH request
2. Enter `{{base_url}}/api/marketplace/items/3/` as the URL (replace 3 with the actual item ID)
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Go to the "Body" tab, select "raw" and "JSON"
6. Enter the request body as shown above
7. Click "Send"

### Delete Item

**Endpoint:** `DELETE {{base_url}}/api/marketplace/items/{id}/`

**Headers:**
```
Authorization: Token {{token}}
```

**Response (204 No Content)**

**Postman Example:**
1. Create a new DELETE request
2. Enter `{{base_url}}/api/marketplace/items/3/` as the URL (replace 3 with the actual item ID)
3. Go to the "Headers" tab
4. Add `Authorization` as key and `Token {{token}}` as value
5. Click "Send"

## Error Handling

The API returns standard HTTP status codes:

- 200: OK
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
  "error": "Detailed error message"
}
```

## Testing Seller and Buyer Roles

In the Agrosmart system, users can have one of two roles:

1. **Buyer**: The default role for all users who register without providing an ID number.
2. **Seller**: Users who have provided an ID number in their profile.

The role determines what actions a user can perform in the marketplace. While the current implementation allows both roles to perform all actions, the system is designed to distinguish between them for future permission enhancements.

### Understanding User Roles

- A user's role is determined by the presence of an `id_number` field in their profile.
- If `id_number` is provided, the user is a seller.
- If `id_number` is not provided (null or empty), the user is a buyer.
- The role is returned in API responses as the `role` field with values "seller" or "buyer".

### Testing as a Buyer

To test the API as a buyer:

1. **Register a Buyer Account**:
   ```json
   {
     "username": "buyer_user",
     "email": "buyer@example.com",
     "password": "SecurePassword123",
     "password2": "SecurePassword123",
     "first_name": "Buyer",
     "last_name": "User",
     "phone_number": "+1234567890"
   }
   ```

   Note: `id_number` is not included in the request, which makes this a buyer account.

2. **Login with the Buyer Account**:
   ```json
   {
     "username": "buyer_user",
     "password": "SecurePassword123"
   }
   ```

3. **Verify the Role**:
   Check that the response includes `"role": "buyer"`.

4. **Use the Marketplace API**:
   - List items
   - Get item details
   - Create new items
   - Update items
   - Delete items

### Testing as a Seller

To test the API as a seller:

1. **Register a Seller Account**:
   ```json
   {
     "username": "seller_user",
     "email": "seller@example.com",
     "password": "SecurePassword123",
     "password2": "SecurePassword123",
     "first_name": "Seller",
     "last_name": "User",
     "phone_number": "+1234567890",
     "id_number": "ID12345"
   }
   ```

   Note: Including the `id_number` field makes this a seller account.

2. **Login with the Seller Account**:
   ```json
   {
     "username": "seller_user",
     "password": "SecurePassword123"
   }
   ```

3. **Verify the Role**:
   Check that the response includes `"role": "seller"`.

4. **Use the Marketplace API**:
   - List items
   - Get item details
   - Create new items
   - Update items
   - Delete items

### Converting a Buyer to a Seller

You can convert a buyer to a seller by updating their profile to include an ID number:

1. **Update the User Profile**:
   ```json
   {
     "id_number": "ID67890"
   }
   ```

2. **Verify the Role Change**:
   - Get the user profile again
   - Check that the response now includes `"role": "seller"`

### Postman Collection for Testing Both Roles

To test both roles in Postman:

1. Create two environments in Postman:
   - "Agrosmart Buyer"
   - "Agrosmart Seller"

2. For each environment, set the following variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (leave empty initially)
   - `username`: "buyer_user" or "seller_user"
   - `password`: "SecurePassword123"

3. Create a folder in your collection for each role:
   - "Buyer Tests"
   - "Seller Tests"

4. In each folder, add the following requests:
   - Register (with appropriate body for buyer or seller)
   - Login
   - Get Profile
   - Create Marketplace Item
   - Update Marketplace Item
   - Delete Marketplace Item

5. Use environment variables in your requests:
   ```
   {{base_url}}/api/auth/login/
   ```

   ```json
   {
     "username": "{{username}}",
     "password": "{{password}}"
   }
   ```

6. After login, use a script to automatically set the token:
   ```javascript
   // In the "Tests" tab of the Login request
   var jsonData = pm.response.json();
   pm.environment.set("token", jsonData.token);
   ```

7. Switch between environments to test as different roles.

## Rate Limiting

API requests are limited to 100 requests per hour per user. If you exceed this limit, you'll receive a 429 Too Many Requests response.

## Creating a Postman Collection

You can create a complete Postman collection for testing all the APIs:

1. In Postman, click "Import" > "Raw text"
2. Copy and paste the following JSON:

```json
{
  "info": {
    "name": "Agrosmart API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"test_user\",\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePassword123\",\n  \"password2\": \"SecurePassword123\",\n  \"first_name\": \"Test\",\n  \"last_name\": \"User\",\n  \"phone_number\": \"+1234567890\",\n  \"id_number\": \"ID12345\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/register/",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "register", ""]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"test_user\",\n  \"password\": \"SecurePassword123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/login/",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "login", ""]
            }
          }
        },
        {
          "name": "Get Profile",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/auth/profile/",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "profile", ""]
            }
          }
        },
        {
          "name": "Update Profile",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"first_name\": \"Updated\",\n  \"last_name\": \"User\",\n  \"phone_number\": \"+9876543210\",\n  \"id_number\": \"ID67890\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/profile/update/",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "profile", "update", ""]
            }
          }
        }
      ]
    },
    {
      "name": "Crop Recommendation",
      "item": [
        {
          "name": "Recommend Crop (Address)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"address\": \"Nairobi, Kenya\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/recommend/",
              "host": ["{{base_url}}"],
              "path": ["api", "recommend", ""]
            }
          }
        },
        {
          "name": "Recommend Crop (Coordinates)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"latitude\": -1.2921,\n  \"longitude\": 36.8219\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/recommend/",
              "host": ["{{base_url}}"],
              "path": ["api", "recommend", ""]
            }
          }
        }
      ]
    },
    {
      "name": "Disease Detection",
      "item": [
        {
          "name": "Detect Disease",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "file",
                  "type": "file",
                  "src": "/path/to/your/image.jpg"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/detector/detect",
              "host": ["{{base_url}}"],
              "path": ["detector", "detect"]
            }
          }
        }
      ]
    },
    {
      "name": "Marketplace",
      "item": [
        {
          "name": "List All Items",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", ""]
            }
          }
        },
        {
          "name": "Get Item by ID",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/1/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", "1", ""]
            }
          }
        },
        {
          "name": "Create Item",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Tomato Seedlings\",\n  \"description\": \"Healthy tomato seedlings ready for transplanting\",\n  \"price\": \"300.00\",\n  \"category\": \"OTHER\",\n  \"quantity\": 200,\n  \"location\": \"Kisumu\",\n  \"contact_info\": \"+254722222222\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", ""]
            }
          }
        },
        {
          "name": "Update Item",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Tomato Seedlings\",\n  \"description\": \"Organic tomato seedlings ready for transplanting\",\n  \"price\": \"350.00\",\n  \"category\": \"OTHER\",\n  \"quantity\": 150,\n  \"location\": \"Kisumu\",\n  \"contact_info\": \"+254722222222\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/3/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", "3", ""]
            }
          }
        },
        {
          "name": "Partially Update Item",
          "request": {
            "method": "PATCH",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"price\": \"375.00\",\n  \"quantity\": 125\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/3/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", "3", ""]
            }
          }
        },
        {
          "name": "Delete Item",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Token {{token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/marketplace/items/3/",
              "host": ["{{base_url}}"],
              "path": ["api", "marketplace", "items", "3", ""]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": "your_auth_token_here"
    }
  ]
}
```

3. Click "Import"
4. Update the `base_url` variable if needed
5. After logging in, update the `token` variable with the token from the login response
