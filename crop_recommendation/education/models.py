from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator


def upload_to(instance, filename):
    return f'education_thumbnails/{filename}'

class Content(models.Model): 
    ARTICLE = 'article'
    YOUTUBE = 'youtube'
    CONTENT_TYPES = [
        (ARTICLE, 'Article'),
        (YOUTUBE, 'YouTube Video'),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CONTENT_TYPES, default=ARTICLE)
    url_or_text = models.TextField()
    
    thumbnail = models.ImageField(  
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='education_posts',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Posts that pass the safety checks are published straight away. If the
    # automatic check could not run, the post waits for an admin to approve it.
    APPROVED = 'approved'
    PENDING = 'pending'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending review'),
        (REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    moderation_note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.ForeignKey(Content, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='education_comments',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    text = models.TextField()
    # Replies are one level deep, like Instagram: a reply always points at a top-level comment
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    # Accounts tagged with @username in the text
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in_comments', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.content.title} (ID: {self.id})"
