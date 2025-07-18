from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid


class User(AbstractUser):
    """
    Custom User model extending AbstractUser
    Adds additional fields for the messaging app
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user"
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's last name"
    )
    password = models.CharField(
        max_length=128,
        help_text="User's password (hashed)"
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="User's phone number"
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('guest', 'Guest'),
            ('host', 'Host'),
            ('admin', 'Admin'),
        ],
        default='guest',
        help_text="User's role in the system"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user was created"
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class Conversation(models.Model):
    """
    Model representing a conversation between users
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the conversation"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        help_text="Users participating in this conversation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the conversation was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the conversation was last updated"
    )
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()[:2]])
        total_participants = self.participants.count()
        if total_participants > 2:
            return f"Conversation: {participant_names} and {total_participants - 2} others"
        return f"Conversation: {participant_names}"
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-sent_at').first()


class Message(models.Model):
    """
    Model representing a message in a conversation
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the message"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversation this message belongs to"
    )
    message_body = models.TextField(
        help_text="Content of the message"
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was sent"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was sent"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the message was last updated"
    )
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['conversation', '-sent_at']),
            models.Index(fields=['sender', '-sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}: {self.message_body[:50]}..."
    
    def save(self, *args, **kwargs):
        """Override save to update conversation's updated_at timestamp"""
        super().save(*args, **kwargs)
        # Update the conversation's updated_at timestamp
        self.conversation.save(update_fields=['updated_at'])
