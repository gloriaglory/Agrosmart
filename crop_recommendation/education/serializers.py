from rest_framework import serializers

import logging

from .mentions import mentioned_users
from .models import Comment, Content
from .moderation import moderate
from . import youtube

logger = logging.getLogger(__name__)
MAX_THUMBNAIL_BYTES = 5 * 1024 * 1024

MAX_COMMENT_LENGTH = 2200  # same limit as Instagram


class CommentAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()
    is_seller = serializers.BooleanField()
    nida_verified = serializers.BooleanField()

    def get_name(self, user):
        return f"{user.first_name} {user.last_name}".strip() or user.username


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)
    mentions = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    likes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'content', 'parent', 'author', 'mentions',
                  'likes_count', 'liked', 'replies', 'created_at']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
        }

    def _user(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_liked(self, obj):
        user = self._user()
        return bool(user) and obj.likes.filter(pk=user.pk).exists()

    def get_replies(self, obj):
        # Only top-level comments carry their replies
        if obj.parent_id:
            return []
        return CommentSerializer(obj.replies.all(), many=True, context=self.context).data

    def validate_text(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(value) > MAX_COMMENT_LENGTH:
            raise serializers.ValidationError(f"Keep comments under {MAX_COMMENT_LENGTH} characters.")
        # Comments are only blocked when clearly inappropriate; if the AI check
        # cannot run they still go through so conversations are not held up.
        decision = moderate(value)
        if decision.blocked:
            raise serializers.ValidationError(decision.reason)
        return value

    def validate(self, attrs):
        parent = attrs.get('parent')
        content = attrs.get('content') or (self.instance.content if self.instance else None)
        if content and content.status != Content.APPROVED:
            raise serializers.ValidationError({'content': "You can comment once this post is published."})
        if parent:
            if parent.content_id != content.id:
                raise serializers.ValidationError({'parent': "Reply must be on the same post."})
            # Replying to a reply attaches to the original comment, like Instagram
            if parent.parent_id:
                attrs['parent'] = parent.parent
        return attrs

    def _save_mentions(self, comment):
        author = comment.author
        comment.mentions.set([u for u in mentioned_users(comment.text) if u != author])

    def create(self, validated_data):
        comment = super().create(validated_data)
        self._save_mentions(comment)
        return comment

    def update(self, instance, validated_data):
        # Only the text can change after posting
        validated_data = {'text': validated_data.get('text', instance.text)}
        comment = super().update(instance, validated_data)
        self._save_mentions(comment)
        return comment


class ContentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    moderation_note = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'title', 'type', 'url_or_text', 'thumbnail', 'author', 'status',
                  'moderation_note', 'comments_count', 'created_at']
        read_only_fields = ['status']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_moderation_note(self, obj):
        # Only the author and admins see why a post is waiting or was rejected
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated and (user.is_staff or obj.author_id == user.id):
            return obj.moderation_note
        return ""

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Add a title.")
        return value

    def validate_thumbnail(self, value):
        if value and value.size > MAX_THUMBNAIL_BYTES:
            raise serializers.ValidationError("Thumbnail must be smaller than 5 MB.")
        return value

    def validate(self, attrs):
        get = lambda field: attrs.get(field, getattr(self.instance, field, None) if self.instance else None)
        kind, title, body = get('type'), get('title') or '', (get('url_or_text') or '').strip()
        if not body:
            raise serializers.ValidationError(
                {'url_or_text': "Add the article text." if kind == Content.ARTICLE else "Add a YouTube link."}
            )

        text_to_check = f"{title}\n\n{body}"
        review_reasons = []

        if kind == Content.YOUTUBE:
            vid = youtube.video_id(body)
            if not vid:
                raise serializers.ValidationError({'url_or_text': "Enter a valid YouTube video link."})
            attrs['url_or_text'] = youtube.canonical_url(vid)
            try:
                info = youtube.video_info(vid)
            except Exception as exc:
                logger.warning("YouTube lookup failed: %s", exc)
                info = {}
                review_reasons.append("video details could not be checked")
            if info is None:
                raise serializers.ValidationError(
                    {'url_or_text': "This video was not found, is private, or does not allow embedding."}
                )
            if info:
                text_to_check += f"\n\nVideo title: {info['title']}\nChannel: {info['channel']}"

        image = None
        thumbnail = attrs.get('thumbnail')
        if thumbnail:
            image = (thumbnail.read(), getattr(thumbnail, 'content_type', None) or 'image/jpeg')
            thumbnail.seek(0)

        decision = moderate(text_to_check, image=image)
        if decision.blocked:
            raise serializers.ValidationError({'detail': decision.reason})
        if decision.action == 'review':
            review_reasons.append(decision.reason.lower())

        request = self.context.get('request')
        is_staff = bool(request and request.user.is_staff)
        if review_reasons and not is_staff:
            attrs['status'] = Content.PENDING
            attrs['moderation_note'] = "Waiting for admin review: " + "; ".join(review_reasons) + "."
        else:
            attrs['status'] = Content.APPROVED
            attrs['moderation_note'] = ""
        return attrs
