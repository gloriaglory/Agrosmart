from django.db.models import Prefetch, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Comment, Content
from .permissions import IsAuthenticatedOrReadOnly, IsAuthorOrAdmin
from .serializers import CommentSerializer, ContentSerializer


def visible_posts(user):
    """Published posts, plus the user's own posts awaiting review. Admins see everything."""
    qs = Content.objects.select_related('author')
    if user.is_authenticated and user.is_staff:
        return qs
    if user.is_authenticated:
        return qs.filter(Q(status=Content.APPROVED) | Q(author=user))
    return qs.filter(status=Content.APPROVED)


class ContentViewSet(viewsets.ModelViewSet):
    """
    Education posts (articles and YouTube videos).
    Logged-in users can post; every post is safety-checked first.
    Only the author or an admin can edit or delete a post.
    """
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return visible_posts(self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Comments on education posts.

    GET ?content=<id> returns that post's top-level comments, each with its replies.
    Anyone can read; logged-in users can comment and like; only authors can delete.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]

    def get_queryset(self):
        reply_qs = Comment.objects.select_related('author').prefetch_related('likes', 'mentions')
        qs = Comment.objects.select_related('author').prefetch_related(
            'likes', 'mentions', Prefetch('replies', queryset=reply_qs)
        )
        qs = qs.filter(content__in=visible_posts(self.request.user))
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
            content = self.request.query_params.get('content')
            if content:
                qs = qs.filter(content_id=content)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like the comment, or remove the like if it is already liked."""
        comment = self.get_object()
        if comment.likes.filter(pk=request.user.pk).exists():
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True
        return Response({'liked': liked, 'likes_count': comment.likes.count()})
