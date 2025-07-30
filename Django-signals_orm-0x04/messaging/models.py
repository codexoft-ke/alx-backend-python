"""
Models for the messaging app.

This module contains the Message and Notification models for implementing
a messaging system with automatic notifications using Django signals.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    """
    Model representing a message between users.
    
    Attributes:
        sender (ForeignKey): The user who sent the message
        receiver (ForeignKey): The user who receives the message
        content (TextField): The message content
        timestamp (DateTimeField): When the message was created
        is_read (BooleanField): Whether the message has been read
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="The user who sent this message"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="The user who receives this message"
    )
    content = models.TextField(
        max_length=1000,
        help_text="The message content"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the message was created"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the message has been read by the receiver"
    )
    edited = models.BooleanField(
        default=False,
        help_text="Whether the message has been edited"
    )
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the message was last edited"
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="The message this is a reply to (for threaded conversations)"
    )
    thread_level = models.PositiveIntegerField(
        default=0,
        help_text="The depth level in the conversation thread (0 for root messages)"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"

    def mark_as_read(self):
        """Mark the message as read."""
        self.is_read = True
        self.save()

    def mark_as_edited(self):
        """Mark the message as edited and update the edited timestamp."""
        self.edited = True
        self.edited_at = timezone.now()
        self.save()

    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.parent_message is not None

    def is_root_message(self):
        """Check if this message is a root message (not a reply)."""
        return self.parent_message is None

    def get_root_message(self):
        """Get the root message of this conversation thread."""
        if self.is_root_message():
            return self
        current = self
        while current.parent_message:
            current = current.parent_message
        return current

    def get_thread_participants(self):
        """Get all users who have participated in this conversation thread."""
        from django.db.models import Q
        root = self.get_root_message()
        
        # Get all messages in this thread
        thread_messages = Message.objects.filter(
            Q(pk=root.pk) | Q(parent_message=root) | 
            Q(parent_message__parent_message=root) |
            Q(parent_message__parent_message__parent_message=root)  # Support up to 3 levels deep
        )
        
        # Get unique participants
        participants = User.objects.filter(
            Q(sent_messages__in=thread_messages) | 
            Q(received_messages__in=thread_messages)
        ).distinct()
        
        return participants

    def get_reply_count(self):
        """Get the total number of replies to this message (including nested replies)."""
        return self.get_all_replies().count()

    def get_direct_replies(self):
        """Get direct replies to this message (using optimized query)."""
        return self.replies.select_related('sender', 'receiver').prefetch_related(
            'replies__sender', 'replies__receiver'
        ).order_by('timestamp')

    def get_all_replies(self):
        """Get all replies to this message recursively (optimized)."""
        from django.db.models import Q
        
        # Build a recursive query to get all replies at any level
        def get_reply_ids(message_id, collected_ids=None):
            if collected_ids is None:
                collected_ids = set()
            
            direct_reply_ids = list(
                Message.objects.filter(parent_message_id=message_id)
                .values_list('id', flat=True)
            )
            
            for reply_id in direct_reply_ids:
                if reply_id not in collected_ids:
                    collected_ids.add(reply_id)
                    get_reply_ids(reply_id, collected_ids)
            
            return collected_ids
        
        reply_ids = get_reply_ids(self.id)
        return Message.objects.filter(id__in=reply_ids).select_related(
            'sender', 'receiver', 'parent_message'
        ).order_by('timestamp')

    def get_conversation_thread(self):
        """Get the entire conversation thread starting from the root message."""
        root = self.get_root_message()
        
        # Get all messages in the thread
        all_messages = [root] + list(root.get_all_replies())
        
        return all_messages

    def save(self, *args, **kwargs):
        """Override save to automatically set thread_level."""
        if self.parent_message:
            self.thread_level = self.parent_message.thread_level + 1
        else:
            self.thread_level = 0
        super().save(*args, **kwargs)

    @classmethod
    def get_threaded_conversations(cls, user, limit=20):
        """
        Get threaded conversations for a user with optimized queries.
        
        Returns root messages with their reply counts and latest activity.
        """
        from django.db.models import Count, Max, Q, Prefetch
        
        # Get root messages where user is sender or receiver
        root_messages = cls.objects.filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True
        ).select_related('sender', 'receiver').annotate(
            reply_count=Count('replies'),
            latest_activity=Max('replies__timestamp')
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver').order_by('timestamp')
            )
        ).order_by('-timestamp')[:limit]
        
        return root_messages

    @classmethod
    def search_in_conversations(cls, user, query, limit=50):
        """Search for messages in user's conversations with threading context."""
        from django.db.models import Q
        
        matching_messages = cls.objects.filter(
            Q(sender=user) | Q(receiver=user),
            content__icontains=query
        ).select_related('sender', 'receiver', 'parent_message').order_by('-timestamp')[:limit]
        
        # Group by conversation thread
        conversations = {}
        for message in matching_messages:
            root = message.get_root_message()
            if root.id not in conversations:
                conversations[root.id] = {
                    'root': root,
                    'matching_messages': []
                }
            conversations[root.id]['matching_messages'].append(message)
        
        return list(conversations.values())


class MessageHistory(models.Model):
    """
    Model to store the history of message edits.
    
    This model keeps track of all previous versions of a message
    whenever it gets edited, allowing users to view edit history.
    
    Attributes:
        message (ForeignKey): The message this history entry belongs to
        old_content (TextField): The previous content before the edit
        edited_by (ForeignKey): The user who made the edit
        edited_at (DateTimeField): When the edit was made
        version (PositiveIntegerField): Version number of this edit
    """
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='history',
        help_text="The message this history entry belongs to"
    )
    old_content = models.TextField(
        max_length=1000,
        help_text="The previous content before the edit"
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_edits',
        help_text="The user who made the edit"
    )
    edited_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the edit was made"
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number of this edit"
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"
        unique_together = ['message', 'version']

    def __str__(self):
        return f"Edit #{self.version} of message #{self.message.id} by {self.edited_by.username}"

    @classmethod
    def create_history_entry(cls, message, old_content, edited_by):
        """
        Create a new history entry for a message edit.
        
        Args:
            message: The message being edited
            old_content: The content before the edit
            edited_by: The user making the edit
        
        Returns:
            MessageHistory: The created history entry
        """
        # Get the next version number
        last_version = cls.objects.filter(message=message).aggregate(
            max_version=models.Max('version')
        )['max_version'] or 0
        
        return cls.objects.create(
            message=message,
            old_content=old_content,
            edited_by=edited_by,
            version=last_version + 1
        )


class Notification(models.Model):
    """
    Model representing a notification for users.
    
    Attributes:
        user (ForeignKey): The user who receives the notification
        message (ForeignKey): The message that triggered this notification
        notification_type (CharField): Type of notification
        is_read (BooleanField): Whether the notification has been read
        created_at (DateTimeField): When the notification was created
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('message_read', 'Message Read'),
        ('message_edited', 'Message Edited'),
        ('user_online', 'User Online'),
        ('user_offline', 'User Offline'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who receives this notification"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="The message that triggered this notification"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='new_message',
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Detailed notification description"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the notification was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()


class UserProfile(models.Model):
    """
    Extended user profile model.
    
    Attributes:
        user (OneToOneField): Link to Django's User model
        is_online (BooleanField): Whether the user is currently online
        last_seen (DateTimeField): When the user was last seen
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    is_online = models.BooleanField(
        default=False,
        help_text="Whether the user is currently online"
    )
    last_seen = models.DateTimeField(
        default=timezone.now,
        help_text="When the user was last seen"
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile for {self.user.username}"

    def set_online(self):
        """Set user as online."""
        self.is_online = True
        self.last_seen = timezone.now()
        self.save()

    def set_offline(self):
        """Set user as offline."""
        self.is_online = False
        self.last_seen = timezone.now()
        self.save()
