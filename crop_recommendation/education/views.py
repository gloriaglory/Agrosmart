from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Content, Comment
from .serializers import ContentSerializer, CommentSerializer
from .permissions import IsAuthenticatedOrReadOnly

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all().order_by('-created_at')
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
