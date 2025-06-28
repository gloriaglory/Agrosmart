from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    RegisterView, 
    LoginView, 
    UserProfileView, 
    UserUpdateView,
    GoogleLogin,
    FacebookLogin,RequestPasswordResetView,VerifyPasswordResetTokenView,ResetPasswordView
    FacebookLogin,
    UpdateIdNumberView
)

urlpatterns = [
    # User registration and authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', obtain_auth_token, name='token_obtain'),

    # Password reset
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', VerifyPasswordResetTokenView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),


    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path("user/idnumber/", UpdateIdNumberView.as_view(), name="update-id-number"),

    # Social authentication
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('facebook/', FacebookLogin.as_view(), name='facebook_login'),
    
    # Include django-allauth URLs
    path('', include('allauth.urls')),
]