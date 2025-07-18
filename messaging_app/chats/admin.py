from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User admin configuration
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'created_at')
        }),
    )
    
    readonly_fields = ('user_id', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Conversation admin configuration
    """
    list_display = ('conversation_id', 'get_participants', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username', 'participants__email')
    ordering = ('-updated_at',)
    readonly_fields = ('conversation_id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',)
    
    def get_participants(self, obj):
        """Display participants in the admin list"""
        return ", ".join([user.username for user in obj.participants.all()[:3]])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Message admin configuration
    """
    list_display = ('message_id', 'sender', 'conversation', 'get_message_preview', 'sent_at')
    list_filter = ('sent_at', 'sender')
    search_fields = ('sender__username', 'message_body', 'conversation__participants__username')
    ordering = ('-sent_at',)
    readonly_fields = ('message_id', 'sent_at', 'created_at', 'updated_at')
    
    def get_message_preview(self, obj):
        """Display message preview in the admin list"""
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    get_message_preview.short_description = 'Message Preview'
