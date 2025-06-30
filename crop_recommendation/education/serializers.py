from rest_framework import serializers
from .models import Content, Comment

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'content', 'parent', 'replies', 'created_at']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
        }

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data


class ContentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = ['id', 'title', 'type', 'url_or_text', 'thumbnail', 'comments', 'created_at']
