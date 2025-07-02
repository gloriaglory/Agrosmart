from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Content, Comment
from .serializers import ContentSerializer, CommentSerializer
from .permissions import IsAuthenticatedOrReadOnly

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all().order_by('-created_at')
    serializer_class = ContentSerializer
    permission_classes = []  # Public API: no authentication required
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        user = None
        request = self.request
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            user = request.user
        else:
            # Try to get user from token if present
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_authenticator = JWTAuthentication()
            header = jwt_authenticator.get_header(request)
            if header is not None:
                validated_token = jwt_authenticator.get_validated_token(header)
                user = jwt_authenticator.get_user(validated_token)
        serializer.save(user=user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer
    permission_classes = []  # Public API: no authentication required

    def perform_create(self, serializer):
        user = None
        request = self.request
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            user = request.user
        else:
            # Try to get user from token if present
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                jwt_authenticator = JWTAuthentication()
                header = jwt_authenticator.get_header(request)
                if header is not None:
                    validated_token = jwt_authenticator.get_validated_token(header)
                    user = jwt_authenticator.get_user(validated_token)
            except Exception:
                user = None
        serializer.save(user=user)
