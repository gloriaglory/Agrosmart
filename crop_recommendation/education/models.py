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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.ForeignKey(Content, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.content.title} (ID: {self.id})"
    
    

