from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    RegisterView, 
    LoginView, 
    UserProfileView, 
    UserUpdateView,
    UpdateIdNumberView,
    VerifyNidaView,
    UserSearchView,
)
from .social import GoogleLogin, FacebookLogin, social_config

urlpatterns = [
    # User registration and authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', obtain_auth_token, name='token_obtain'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path("user/idnumber/", UpdateIdNumberView.as_view(), name="update-id-number"),
    path("nida/verify/", VerifyNidaView.as_view(), name="nida-verify"),
    path("users/search/", UserSearchView.as_view(), name="user-search"),
    
    # Social authentication (website posts the provider's access token here)
    path('social/config/', social_config, name='social_config'),
    path('google/', GoogleLogin.as_view(), name='google_token_login'),
    path('facebook/', FacebookLogin.as_view(), name='facebook_token_login'),
    
    # Include django-allauth URLs
    path('', include('allauth.urls')),
]