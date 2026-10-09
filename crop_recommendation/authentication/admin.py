from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for the User model.
    Adds phone_number and id_number fields to the admin interface.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'id_number', 'nida_verified', 'role', 'is_staff')
    list_filter = ('nida_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'id_number')
    actions = ['mark_nida_verified', 'mark_nida_unverified']

    @admin.action(description="Mark NIDA as verified (after checking the ID manually)")
    def mark_nida_verified(self, request, queryset):
        updated = queryset.exclude(id_number__isnull=True).update(nida_verified=True)
        self.message_user(request, f"{updated} user(s) marked as NIDA verified.")

    @admin.action(description="Mark NIDA as not verified")
    def mark_nida_unverified(self, request, queryset):
        updated = queryset.update(nida_verified=False)
        self.message_user(request, f"{updated} user(s) marked as not verified.")

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'id_number', 'nida_verified')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'phone_number', 'id_number'),
        }),
    )
