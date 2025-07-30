"""
Django admin configuration for the messaging app.

This module registers the Message, Notification, and UserProfile models
with the Django admin interface, making them manageable through the admin panel.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Message, Notification, UserProfile, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Message model.
    
    Provides a comprehensive interface for managing messages including
    filtering, searching, and bulk actions.
    """
    list_display = [
        'id',
        'sender_link',
        'receiver_link', 
        'content_preview',
        'timestamp',
        'is_read_status',
        'edit_status',
        'history_count',
        'notification_count'
    ]
    list_filter = [
        'is_read',
        'edited',
        'timestamp',
        'edited_at',
        'sender__username',
        'receiver__username'
    ]
    search_fields = [
        'sender__username',
        'receiver__username',
        'content'
    ]
    readonly_fields = [
        'timestamp',
        'edited_at',
        'history_count',
        'notification_count'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    list_per_page = 25

    def sender_link(self, obj):
        """Create a clickable link to the sender's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)
    sender_link.short_description = 'Sender'

    def receiver_link(self, obj):
        """Create a clickable link to the receiver's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.receiver.id])
        return format_html('<a href="{}">{}</a>', url, obj.receiver.username)
    receiver_link.short_description = 'Receiver'

    def content_preview(self, obj):
        """Show a truncated preview of the message content."""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Content Preview'

    def is_read_status(self, obj):
        """Display read status with colored indicator."""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Unread</span>'
        )
    is_read_status.short_description = 'Status'

    def edit_status(self, obj):
        """Display edit status with colored indicator."""
        if obj.edited:
            return format_html(
                '<span style="color: orange; font-weight: bold;">✏️ Edited</span>'
            )
        return format_html(
            '<span style="color: gray;">📝 Original</span>'
        )
    edit_status.short_description = 'Edit Status'

    def history_count(self, obj):
        """Show the number of edit history entries for this message."""
        count = obj.history.count()
        if count > 0:
            return format_html(
                '<a href="/admin/messaging/messagehistory/?message__id={}">{} edit{}</a>',
                obj.id, count, 's' if count != 1 else ''
            )
        return "No edits"
    history_count.short_description = 'Edit History'

    def notification_count(self, obj):
        """Show the number of notifications generated for this message."""
        count = obj.notifications.count()
        return f"{count} notification{'s' if count != 1 else ''}"
    notification_count.short_description = 'Notifications'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Bulk action to mark selected messages as read."""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f'{updated} message{"s" if updated != 1 else ""} marked as read.'
        )
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        """Bulk action to mark selected messages as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f'{updated} message{"s" if updated != 1 else ""} marked as unread.'
        )
    mark_as_unread.short_description = "Mark selected messages as unread"


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the MessageHistory model.
    
    Provides an interface for viewing message edit history.
    """
    list_display = [
        'id',
        'message_link',
        'version',
        'old_content_preview',
        'edited_by_link',
        'edited_at'
    ]
    list_filter = [
        'edited_at',
        'version',
        'edited_by__username'
    ]
    search_fields = [
        'old_content',
        'message__content',
        'edited_by__username'
    ]
    readonly_fields = [
        'message',
        'old_content',
        'edited_by',
        'edited_at',
        'version'
    ]
    ordering = ['-edited_at']
    list_per_page = 25

    def message_link(self, obj):
        """Create a clickable link to the related message."""
        url = reverse('admin:messaging_message_change', args=[obj.message.id])
        return format_html('<a href="{}">Message #{}</a>', url, obj.message.id)
    message_link.short_description = 'Message'

    def edited_by_link(self, obj):
        """Create a clickable link to the user who made the edit."""
        url = reverse('admin:auth_user_change', args=[obj.edited_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.edited_by.username)
    edited_by_link.short_description = 'Edited By'

    def old_content_preview(self, obj):
        """Show a truncated preview of the old content."""
        if len(obj.old_content) > 50:
            return f"{obj.old_content[:50]}..."
        return obj.old_content
    old_content_preview.short_description = 'Old Content Preview'

    def has_add_permission(self, request):
        """Disable adding MessageHistory entries manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing MessageHistory entries."""
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    
    Provides tools for managing user notifications with filtering and search capabilities.
    """
    list_display = [
        'id',
        'user_link',
        'notification_type',
        'title',
        'message_link',
        'is_read_status',
        'created_at'
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
        'user__username'
    ]
    search_fields = [
        'user__username',
        'title',
        'description',
        'message__content'
    ]
    readonly_fields = [
        'created_at',
        'message_preview'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25

    def user_link(self, obj):
        """Create a clickable link to the user's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def message_link(self, obj):
        """Create a clickable link to the related message."""
        if obj.message:
            url = reverse('admin:messaging_message_change', args=[obj.message.id])
            return format_html('<a href="{}">Message #{}</a>', url, obj.message.id)
        return "No message"
    message_link.short_description = 'Related Message'

    def is_read_status(self, obj):
        """Display read status with colored indicator."""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Unread</span>'
        )
    is_read_status.short_description = 'Status'

    def message_preview(self, obj):
        """Show preview of the related message content."""
        if obj.message:
            content = obj.message.content
            if len(content) > 100:
                return f"{content[:100]}..."
            return content
        return "No related message"
    message_preview.short_description = 'Message Preview'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Bulk action to mark selected notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f'{updated} notification{"s" if updated != 1 else ""} marked as read.'
        )
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        """Bulk action to mark selected notifications as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f'{updated} notification{"s" if updated != 1 else ""} marked as unread.'
        )
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    
    Provides management interface for user profiles and online status.
    """
    list_display = [
        'user_link',
        'online_status',
        'last_seen',
        'messages_sent_count',
        'messages_received_count',
        'notifications_count'
    ]
    list_filter = [
        'is_online',
        'last_seen'
    ]
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = [
        'messages_sent_count',
        'messages_received_count',
        'notifications_count'
    ]
    date_hierarchy = 'last_seen'
    ordering = ['-last_seen']

    def user_link(self, obj):
        """Create a clickable link to the user's admin page."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def online_status(self, obj):
        """Display online status with colored indicator."""
        if obj.is_online:
            return format_html(
                '<span style="color: green; font-weight: bold;">🟢 Online</span>'
            )
        return format_html(
            '<span style="color: gray; font-weight: bold;">⚫ Offline</span>'
        )
    online_status.short_description = 'Status'

    def messages_sent_count(self, obj):
        """Count of messages sent by this user."""
        return obj.user.sent_messages.count()
    messages_sent_count.short_description = 'Messages Sent'

    def messages_received_count(self, obj):
        """Count of messages received by this user."""
        return obj.user.received_messages.count()
    messages_received_count.short_description = 'Messages Received'

    def notifications_count(self, obj):
        """Count of notifications for this user."""
        return obj.user.notifications.count()
    notifications_count.short_description = 'Notifications'

    actions = ['set_online', 'set_offline']

    def set_online(self, request, queryset):
        """Bulk action to set selected users as online."""
        for profile in queryset:
            profile.set_online()
        count = queryset.count()
        self.message_user(
            request,
            f'{count} user{"s" if count != 1 else ""} set as online.'
        )
    set_online.short_description = "Set selected users as online"

    def set_offline(self, request, queryset):
        """Bulk action to set selected users as offline."""
        for profile in queryset:
            profile.set_offline()
        count = queryset.count()
        self.message_user(
            request,
            f'{count} user{"s" if count != 1 else ""} set as offline.'
        )
    set_offline.short_description = "Set selected users as offline"


# Customize admin site headers
admin.site.site_header = "Messaging System Administration"
admin.site.site_title = "Messaging Admin"
admin.site.index_title = "Welcome to Messaging System Administration"
