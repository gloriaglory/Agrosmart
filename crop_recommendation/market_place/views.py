from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from authentication.serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer
from authentication.models import PasswordResetToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .models import MarketplaceItem
from .serializers import MarketplaceItemSerializer

User = get_user_model()

# Create your views here.
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    Allows authentication with either username or email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Get credentials from request
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        if not username_or_email or not password:
            return Response(
                {"error": "Please provide both username/email and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to authenticate with username
        user = authenticate(username=username_or_email, password=password)

        # If authentication with username fails, try with email
        if user is None:
            # Check if a user with this email exists
            try:
                user_obj = User.objects.get(email=username_or_email)
                # If user exists, try to authenticate with the username
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            })

        return Response(
            {"error": "Invalid credentials. Please check your username/email and password."},
            status=status.HTTP_400_BAD_REQUEST
        )



class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating user profile.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return updated user data with role
        return Response(UserSerializer(instance).data)




class RequestPasswordResetView(APIView):
    """
    API endpoint to request a password reset.
    Sends an email with a password reset link.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return Response(
                {"message": "If your email exists in our system, you will receive a password reset link."},
                status=status.HTTP_200_OK
            )

        # Generate a token
        reset_token = PasswordResetToken.generate_token(user)

        # Construct the reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"

        # Send email with reset link
        send_mail(
            subject="Reset Your Agrosmart Password",
            message=f"Please use the following link to reset your password: {reset_url}\n\nThis link is valid for 24 hours.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"message": "If your email exists in our system, you will receive a password reset link."},
            status=status.HTTP_200_OK
        )


class VerifyPasswordResetTokenView(APIView):
    """
    API endpoint to verify a password reset token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
            if not reset_token.is_valid():
                return Response(
                    {"error": "Token has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {"message": "Token is valid", "email": reset_token.user.email},
                status=status.HTTP_200_OK
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    """
    API endpoint to reset a password using a token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if not token or not password or not password2:
            return Response(
                {"error": "Token, password, and password confirmation are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password2:
            return Response(
                {"error": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
            if not reset_token.is_valid():
                return Response(
                    {"error": "Token has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update user's password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class GoogleLogin(SocialLoginView):
    """
    API endpoint for Google social login.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/api/auth/google/callback/"
    client_class = OAuth2Client


class FacebookLogin(SocialLoginView):
    """
    API endpoint for Facebook social login.
    """
    adapter_class = FacebookOAuth2Adapter
    callback_url = "http://localhost:8000/api/auth/facebook/callback/"
    client_class = OAuth2Client


class MarketplaceItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for marketplace items.
    Allows listing, creating, updating, and deleting marketplace items.
    """
    queryset = MarketplaceItem.objects.all()
    serializer_class = MarketplaceItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
