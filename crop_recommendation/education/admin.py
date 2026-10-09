from django.contrib import admin

from .models import Comment, Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'author', 'status', 'moderation_note', 'created_at')
    list_filter = ('status', 'type')
    search_fields = ('title', 'url_or_text', 'author__username')
    actions = ['approve', 'reject']

    @admin.action(description="Approve and publish selected posts")
    def approve(self, request, queryset):
        updated = queryset.update(status=Content.APPROVED, moderation_note="")
        self.message_user(request, f"{updated} post(s) published.")

    @admin.action(description="Reject selected posts")
    def reject(self, request, queryset):
        updated = queryset.update(status=Content.REJECTED, moderation_note="Rejected by an admin.")
        self.message_user(request, f"{updated} post(s) rejected.")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'content', 'parent', 'created_at')
    search_fields = ('text', 'author__username')
    raw_id_fields = ('content', 'parent', 'author')
