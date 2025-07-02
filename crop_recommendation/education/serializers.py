from rest_framework import serializers
from .models import Content, Comment

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.id if obj.user else None

    class Meta:
        model = Comment
        fields = ['id', 'text', 'content', 'parent', 'replies', 'created_at', 'user']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
        }

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data


class ContentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.id if obj.user else None

    class Meta:
        model = Content
        fields = '__all__'
        # 'comments' and 'user' are added as extra fields by the serializer
