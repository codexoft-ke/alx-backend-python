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
