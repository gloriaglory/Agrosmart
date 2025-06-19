# API Documentation

## Overview
This document provides brief documentation for the Agrosmart API, focusing on authentication and API usage.

## Installation and Setup

### Requirements
- Python 3.8+
- Django 4.2+
- Required packages: django-rest-framework, django-allauth, dj-rest-auth

### Quick Setup
1. Install required packages:
   ```bash
   pip install django django-rest-framework django-allauth dj-rest-auth
   ```

2. Add the following to your INSTALLED_APPS in settings.py:
   ```python
   INSTALLED_APPS = [
       # Django apps
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django.contrib.sites',

       # Third-party apps
       'rest_framework',
       'rest_framework.authtoken',
       'allauth',
       'allauth.account',
       'allauth.socialaccount',
       'allauth.socialaccount.providers.google',
       'allauth.socialaccount.providers.facebook',

       # Your apps
       'authentication',
   ]
   ```

3. Configure authentication settings:
   ```python
   # Custom user model (if using)
   AUTH_USER_MODEL = 'authentication.User'

   # Django AllAuth settings
   SITE_ID = 1
   AUTHENTICATION_BACKENDS = [
       'django.contrib.auth.backends.ModelBackend',
       'allauth.account.auth_backends.AuthenticationBackend',
   ]

   # REST Framework settings
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.TokenAuthentication',
           'rest_framework.authentication.SessionAuthentication',
       ],
   }
   ```

## Authentication

### CSRF Protection
Django uses CSRF (Cross-Site Request Forgery) protection for security. When making POST, PUT, PATCH, or DELETE requests to the API, you need to include a CSRF token in your request. There are several ways to handle this:

1. **For browser-based applications**:
   - Get the CSRF token from the cookie named `csrftoken`
   - Include it in the request headers as `X-CSRFToken`
   ```javascript
   // Example JavaScript code to include CSRF token
   const csrftoken = document.cookie.split('; ')
     .find(row => row.startsWith('csrftoken='))
     ?.split('=')[1];

   fetch('/api/auth/register/', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRFToken': csrftoken,
     },
     body: JSON.stringify(userData),
   });
   ```

2. **For non-browser applications**:
   - Use token authentication instead of session authentication
   - Include the token in the `Authorization` header
   ```
   Authorization: Token your_auth_token
   ```

3. **For testing with tools like Postman or curl**:
   - First make a GET request to any page to get the CSRF token from the response cookies
   - Then include that token in subsequent POST requests

### User Roles
- **Buyer**: Default role for all users
- **Seller**: Users who have provided an ID number in their profile

### Traditional Authentication
1. Register a new account by sending a POST request to `/api/auth/register/`:
   ```json
   {
     "username": "your_username",
     "email": "your_email@example.com",
     "password": "your_password",
     "password2": "your_password",
     "first_name": "Your",
     "last_name": "Name",
     "phone_number": "+1234567890"
   }
   ```

2. Login by sending a POST request to `/api/auth/login/`:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

3. The response will include user data and an authentication token:
   ```json
   {
     "user": {
       "id": 1,
       "username": "your_username",
       "email": "your_email@example.com",
       "first_name": "Your",
       "last_name": "Name",
       "phone_number": "+1234567890",
       "id_number": null,
       "role": "buyer"
     },
     "token": "your_auth_token"
   }
   ```

4. Include the token in the Authorization header for subsequent requests:
   ```
   Authorization: Token your_auth_token
   ```

### Social Authentication

#### Setup Google Authentication
1. Create a Google OAuth 2.0 client ID at [Google Developer Console](https://console.developers.google.com/)
2. Configure the OAuth consent screen
3. Create OAuth client ID (Web application)
4. Add authorized redirect URIs: `http://yourdomain.com/api/auth/google/callback/`
5. In Django admin, add a new Social Application:
   - Provider: Google
   - Name: Google
   - Client ID: Your Google client ID
   - Secret key: Your Google client secret
   - Sites: Add your site

#### Setup Facebook Authentication
1. Create a Facebook App at [Facebook Developer Portal](https://developers.facebook.com/)
2. Add Facebook Login product to your app
3. Configure Valid OAuth Redirect URIs: `http://yourdomain.com/api/auth/facebook/callback/`
4. In Django admin, add a new Social Application:
   - Provider: Facebook
   - Name: Facebook
   - Client ID: Your Facebook app ID
   - Secret key: Your Facebook app secret
   - Sites: Add your site

#### Using Social Authentication
1. For Google authentication:
   - Frontend: Redirect users to `/api/auth/google/`
   - After authentication, users will be redirected to your callback URL with a token

2. For Facebook authentication:
   - Frontend: Redirect users to `/api/auth/facebook/`
   - After authentication, users will be redirected to your callback URL with a token

3. Example Flutter implementation (Dart):
   ```dart
   // In your Flutter app
   import 'package:flutter/material.dart';
   import 'package:http/http.dart' as http;
   import 'package:shared_preferences/shared_preferences.dart';
   import 'package:url_launcher/url_launcher.dart';
   import 'package:flutter_web_auth/flutter_web_auth.dart';

   class SocialAuthService {
     // Google login
     Future<void> googleLogin() async {
       final Uri url = Uri.parse('http://yourdomain.com/api/auth/google/');
       if (await canLaunchUrl(url)) {
         await launchUrl(url);
       } else {
         throw 'Could not launch $url';
       }
     }

     // Facebook login
     Future<void> facebookLogin() async {
       final Uri url = Uri.parse('http://yourdomain.com/api/auth/facebook/');
       if (await canLaunchUrl(url)) {
         await launchUrl(url);
       } else {
         throw 'Could not launch $url';
       }
     }

     // Handle the callback
     Future<void> handleSocialAuthCallback(String responseUrl) async {
       // Extract token from URL or response
       final String token = extractTokenFromResponse(responseUrl);

       // Store token for future API requests
       final prefs = await SharedPreferences.getInstance();
       await prefs.setString('authToken', token);
     }

     String extractTokenFromResponse(String url) {
       // Implementation to extract token from URL
       // This will depend on your specific response format
       return url.split('token=')[1].split('&')[0];
     }
   }
   ```

4. Example React JS implementation:
   ```jsx
   // In your React app
   import React from 'react';
   import axios from 'axios';

   const SocialAuth = () => {
     // Google login
     const googleLogin = () => {
       window.location.href = 'http://yourdomain.com/api/auth/google/';
     };

     // Facebook login
     const facebookLogin = () => {
       window.location.href = 'http://yourdomain.com/api/auth/facebook/';
     };

     // Handle the callback
     const handleSocialAuthCallback = () => {
       // Get the current URL
       const urlParams = new URLSearchParams(window.location.search);
       const token = urlParams.get('token');

       if (token) {
         // Store token for future API requests
         localStorage.setItem('authToken', token);

         // Use the token for authenticated requests
         axios.defaults.headers.common['Authorization'] = `Token ${token}`;

         // Redirect to profile or home page
         window.location.href = '/profile';
       }
     };

     return (
       <div>
         <button onClick={googleLogin}>Login with Google</button>
         <button onClick={facebookLogin}>Login with Facebook</button>
       </div>
     );
   };

   export default SocialAuth;
   ```

## API Endpoints Reference

### User Management API

All user management endpoints are prefixed with `/api/auth/`.

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/auth/register/` | POST | Register a new user | None |
| `/api/auth/login/` | POST | Login with username/password | None |
| `/api/auth/profile/` | GET | Get user profile | Required |
| `/api/auth/profile/update/` | PUT/PATCH | Update user profile | Required |
| `/api/auth/google/` | GET | Initiate Google OAuth login | None |
| `/api/auth/facebook/` | GET | Initiate Facebook OAuth login | None |

**Note**: Adding an ID number to a user profile automatically changes the user's role from "buyer" to "seller".

### Marketplace API

All marketplace endpoints are prefixed with `/api/marketplace/`.

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/marketplace/items/` | GET | List all marketplace items | Optional |
| `/api/marketplace/items/{id}/` | GET | Get a specific item by ID | Optional |
| `/api/marketplace/items/` | POST | Create a new marketplace item | Required |
| `/api/marketplace/items/{id}/` | PUT | Update an existing item (full update) | Required |
| `/api/marketplace/items/{id}/` | PATCH | Partially update an item | Required |
| `/api/marketplace/items/{id}/` | DELETE | Delete an item | Required |

#### Item Object Structure
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

#### Creating/Updating Items
When creating or updating items, include the following fields in your request:
- `name` (string): Item name
- `description` (string): Item description
- `price` (decimal): Item price
- `category` (string): Item category (default: "OTHER")
- `quantity` (integer): Available quantity
- `location` (string): Item location
- `contact_info` (string): Contact information for the seller

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

## Rate Limiting
API requests are limited to 100 requests per hour per user. If you exceed this limit, you'll receive a 429 Too Many Requests response.

## Testing the API

A file named `api_testing.http` is provided in the project root directory. This file contains HTTP requests for testing all API endpoints.

### Using the API Testing File

1. Open the `api_testing.http` file in an HTTP client tool like VS Code's REST Client extension.
2. Replace the `@authToken` variable with an actual authentication token obtained from login.
3. Execute the requests in sequence to test the API functionality.

### Environment Setup for Testing

If you're using VS Code's REST Client extension, you can set up environment variables in several ways:

1. Create a `.env` file in the same directory with your variables:
   ```
   @baseUrl = http://localhost:8000
   @authToken = your_actual_token_here
   ```

2. Use the "REST Client: Switch Environment" command to select an environment.

3. Right-click on a request and select "Run Request" to execute without environment.

## Contact
For any questions or issues with the API, please contact support@agrosmart.com.
