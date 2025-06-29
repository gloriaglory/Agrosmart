# Password Reset Documentation for Flutter App

## Overview

This document provides comprehensive instructions on implementing password reset functionality in the Flutter app for the Agrosmart platform. The password reset flow allows users to securely reset their passwords when they forget them.

## Backend API Endpoints

The backend provides the following RESTful API endpoints for password reset:

1. **Request Password Reset**
   - **Endpoint**: `/api/auth/password-reset/request/`
   - **Method**: POST
   - **Request Body**:
     ```json
     {
       "email": "user@example.com"
     }
     ```
   - **Response**:
     ```json
     {
       "message": "If your email exists in our system, you will receive a password reset link."
     }
     ```
   - **Description**: Initiates the password reset process by sending an email with a reset link to the user's email address.

2. **Verify Password Reset Token**
   - **Endpoint**: `/api/auth/password-reset/verify/`
   - **Method**: POST
   - **Request Body**:
     ```json
     {
       "token": "reset-token-from-email"
     }
     ```
   - **Response (Success)**:
     ```json
     {
       "message": "Token is valid",
       "email": "user@example.com"
     }
     ```
   - **Response (Error)**:
     ```json
     {
       "error": "Token has expired"
     }
     ```
     or
     ```json
     {
       "error": "Invalid token"
     }
     ```
   - **Description**: Verifies if a password reset token is valid and not expired.

3. **Reset Password**
   - **Endpoint**: `/api/auth/password-reset/confirm/`
   - **Method**: POST
   - **Request Body**:
     ```json
     {
       "token": "reset-token-from-email",
       "password": "new-password",
       "password2": "new-password"
     }
     ```
   - **Response (Success)**:
     ```json
     {
       "message": "Password has been reset successfully"
     }
     ```
   - **Response (Error)**:
     ```json
     {
       "error": "Passwords do not match"
     }
     ```
     or
     ```json
     {
       "error": "Token has expired"
     }
     ```
     or
     ```json
     {
       "error": "Invalid token"
     }
     ```
   - **Description**: Resets the user's password using the provided token.

## Implementation in Flutter

### 1. Create API Service Methods

Add the following methods to your API service class:

```dart
// In api_service.dart or similar file
import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  final String baseUrl = 'https://your-api-url.com/api';
  final Map<String, String> headers = {
    'Content-Type': 'application/json',
  };

  // Request password reset
  Future<void> requestPasswordReset(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/password-reset/request/'),
        headers: headers,
        body: jsonEncode({'email': email}),
      );
      return _processResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Verify password reset token
  Future<Map<String, dynamic>> verifyResetToken(String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/password-reset/verify/'),
        headers: headers,
        body: jsonEncode({'token': token}),
      );
      return _processResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Reset password
  Future<void> resetPassword(String token, String password, String password2) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/password-reset/confirm/'),
        headers: headers,
        body: jsonEncode({
          'token': token,
          'password': password,
          'password2': password2
        }),
      );
      return _processResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Process HTTP response
  dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isNotEmpty) {
        return jsonDecode(response.body);
      }
      return null;
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(errorData['error'] ?? 'An error occurred');
    }
  }

  // Error handling
  Exception _handleError(dynamic error) {
    if (error is http.ClientException) {
      return Exception('Network error: ${error.message}');
    }
    return error is Exception ? error : Exception('An unexpected error occurred');
  }
}
```

### 2. Create Password Reset Screens

#### Forgot Password Screen

```dart
import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _authService = AuthService();
  bool _isLoading = false;
  String? _errorMessage;
  bool _emailSent = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _requestPasswordReset() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _authService.requestPasswordReset(_emailController.text);
      setState(() {
        _emailSent = true;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Forgot Password')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: _emailSent
            ? _buildSuccessMessage()
            : _buildRequestForm(),
      ),
    );
  }

  Widget _buildRequestForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Enter your email address and we\'ll send you a link to reset your password.',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 24),
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email',
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.emailAddress,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your email';
              }
              if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                return 'Please enter a valid email';
              }
              return null;
            },
          ),
          SizedBox(height: 16),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red),
              ),
            ),
          ElevatedButton(
            onPressed: _isLoading ? null : _requestPasswordReset,
            child: _isLoading
                ? CircularProgressIndicator(color: Colors.white)
                : Text('Send Reset Link'),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessMessage() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle, color: Colors.green, size: 64),
          SizedBox(height: 16),
          Text(
            'Reset Link Sent',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          Text(
            'If your email exists in our system, you will receive a password reset link shortly.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Back to Login'),
          ),
        ],
      ),
    );
  }
}
```

#### Reset Password Screen

```dart
import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  final String token;

  ResetPasswordScreen({required this.token});

  @override
  _ResetPasswordScreenState createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _authService = AuthService();
  bool _isLoading = false;
  bool _isTokenValid = false;
  bool _isVerifying = true;
  String? _errorMessage;
  String? _userEmail;
  bool _resetSuccess = false;

  @override
  void initState() {
    super.initState();
    _verifyToken();
  }

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _verifyToken() async {
    try {
      final response = await _authService.verifyResetToken(widget.token);
      setState(() {
        _isTokenValid = true;
        _userEmail = response['email'];
        _isVerifying = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isTokenValid = false;
        _isVerifying = false;
      });
    }
  }

  Future<void> _resetPassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _authService.resetPassword(
        widget.token,
        _passwordController.text,
        _confirmPasswordController.text,
      );
      setState(() {
        _resetSuccess = true;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Reset Password')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: _isVerifying
            ? _buildVerifyingToken()
            : _isTokenValid
                ? _resetSuccess
                    ? _buildSuccessMessage()
                    : _buildResetForm()
                : _buildInvalidToken(),
      ),
    );
  }

  Widget _buildVerifyingToken() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Verifying reset token...'),
        ],
      ),
    );
  }

  Widget _buildInvalidToken() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error, color: Colors.red, size: 64),
          SizedBox(height: 16),
          Text(
            'Invalid or Expired Token',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          Text(
            _errorMessage ?? 'The password reset link is invalid or has expired.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pushReplacementNamed(context, '/forgot-password'),
            child: Text('Request New Reset Link'),
          ),
        ],
      ),
    );
  }

  Widget _buildResetForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Reset Password',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            'Create a new password for ${_userEmail ?? 'your account'}',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 24),
          TextFormField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'New Password',
              border: OutlineInputBorder(),
            ),
            obscureText: true,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a new password';
              }
              if (value.length < 8) {
                return 'Password must be at least 8 characters';
              }
              return null;
            },
          ),
          SizedBox(height: 16),
          TextFormField(
            controller: _confirmPasswordController,
            decoration: InputDecoration(
              labelText: 'Confirm New Password',
              border: OutlineInputBorder(),
            ),
            obscureText: true,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please confirm your password';
              }
              if (value != _passwordController.text) {
                return 'Passwords do not match';
              }
              return null;
            },
          ),
          SizedBox(height: 16),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red),
              ),
            ),
          ElevatedButton(
            onPressed: _isLoading ? null : _resetPassword,
            child: _isLoading
                ? CircularProgressIndicator(color: Colors.white)
                : Text('Reset Password'),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessMessage() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle, color: Colors.green, size: 64),
          SizedBox(height: 16),
          Text(
            'Password Reset Successful',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          Text(
            'Your password has been reset successfully. You can now log in with your new password.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pushReplacementNamed(context, '/login'),
            child: Text('Go to Login'),
          ),
        ],
      ),
    );
  }
}
```

### 3. Update Navigation and Routes

Add the password reset screens to your app's routes:

```dart
// In your main.dart or routes.dart file
import 'package:flutter/material.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/reset_password_screen.dart';
import 'screens/login_screen.dart';

class AppRoutes {
  static Map<String, WidgetBuilder> getRoutes() {
    return {
      '/login': (context) => LoginScreen(),
      '/forgot-password': (context) => ForgotPasswordScreen(),
      // For the reset password screen, you'll need to handle the token from the URL
    };
  }

  // Handle deep links for password reset
  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    if (settings.name?.startsWith('/reset-password/') ?? false) {
      final token = settings.name!.split('/').last;
      return MaterialPageRoute(
        builder: (context) => ResetPasswordScreen(token: token),
      );
    }
    return null;
  }
}
```

### 4. Add Link to Forgot Password in Login Screen

Update your login screen to include a "Forgot Password?" link:

```
// In your login_screen.dart
// Add this inside your login form
TextButton(
  onPressed: () => Navigator.pushNamed(context, '/forgot-password'),
  child: Text('Forgot Password?'),
)
```

### 5. Handle Deep Links for Password Reset

To handle the password reset links that users receive in their email, you need to set up deep linking in your Flutter app:

#### Update AndroidManifest.xml

```
<manifest ...>
  <application ...>
    <activity ...>
      <!-- ... other intent filters ... -->
      <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
          android:scheme="https"
          android:host="your-app-domain.com"
          android:pathPrefix="/reset-password" />
      </intent-filter>
    </activity>
  </application>
</manifest>
```

#### Update Info.plist (iOS)

```
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleTypeRole</key>
    <string>Editor</string>
    <key>CFBundleURLName</key>
    <string>com.yourdomain.app</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>your-app-scheme</string>
    </array>
  </dict>
</array>
```

#### Handle Deep Links in Flutter

```dart
import 'package:flutter/material.dart';
import 'package:uni_links/uni_links.dart';
import 'dart:async';

class DeepLinkHandler extends StatefulWidget {
  final Widget child;

  DeepLinkHandler({required this.child});

  @override
  _DeepLinkHandlerState createState() => _DeepLinkHandlerState();
}

class _DeepLinkHandlerState extends State<DeepLinkHandler> {
  StreamSubscription? _sub;

  @override
  void initState() {
    super.initState();
    _handleIncomingLinks();
    _handleInitialUri();
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  void _handleIncomingLinks() {
    _sub = uriLinkStream.listen((Uri? uri) {
      if (uri != null) {
        _handleLink(uri);
      }
    }, onError: (err) {
      // Handle exception
      print('Error handling incoming link: $err');
    });
  }

  Future<void> _handleInitialUri() async {
    try {
      final uri = await getInitialUri();
      if (uri != null) {
        _handleLink(uri);
      }
    } catch (e) {
      // Handle exception
      print('Error handling initial link: $e');
    }
  }

  void _handleLink(Uri uri) {
    final pathSegments = uri.pathSegments;
    if (pathSegments.length >= 2 && pathSegments[0] == 'reset-password') {
      final token = pathSegments[1];
      // Navigate to reset password screen with token
      Navigator.of(context).pushNamed('/reset-password/$token');
    }
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

// In your main.dart
void main() {
  runApp(
    DeepLinkHandler(
      child: MyApp(),
    ),
  );
}
```

## Best Practices

1. **Security**:
   - Always use HTTPS for API requests
   - Implement rate limiting on password reset requests to prevent abuse
   - Ensure tokens are single-use and have a short expiration time (24 hours is standard)
   - Don't reveal whether an email exists in the system in error messages

2. **User Experience**:
   - Provide clear feedback at each step of the process
   - Include password strength indicators when setting a new password
   - Implement proper form validation with helpful error messages
   - Consider adding biometric authentication as an alternative to password login

3. **Error Handling**:
   - Handle network errors gracefully
   - Provide clear error messages that don't reveal sensitive information
   - Implement retry mechanisms for network failures

4. **Testing**:
   - Test the entire flow from end to end
   - Test with various email providers
   - Test edge cases like expired tokens, invalid tokens, etc.
   - Test on different devices and screen sizes

## Troubleshooting

### Common Issues and Solutions

1. **Reset email not received**:
   - Check spam/junk folder
   - Verify the email address is correct
   - Check if the email service is configured correctly on the backend

2. **Token invalid or expired**:
   - Request a new password reset link
   - Check if the token has been used already (tokens are single-use)
   - Verify the token hasn't expired (valid for 24 hours)

3. **Deep linking not working**:
   - Ensure the app's deep link configuration is correct
   - Verify the link format matches what's expected by the app
   - Check if the app is installed on the device

4. **Network errors**:
   - Check internet connection
   - Verify the API base URL is correct
   - Check if the backend server is running

## Conclusion

Implementing a secure and user-friendly password reset flow is crucial for any application. By following this guide, you can create a robust password reset system in your Flutter app that integrates with the Agrosmart backend API.

For any additional questions or issues, please contact the development team.
