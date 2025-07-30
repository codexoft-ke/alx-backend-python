"""
Advanced threaded conversation models for Django Chat.

This module contains optimized models and managers for handling
threaded conversations with advanced ORM techniques.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Max, Prefetch


class ConversationManager(models.Manager):
    """Custom manager for optimized conversation queries."""
    
    def get_threaded_conversations(self, user, limit=20):
        """
        Get threaded conversations for a user with optimized queries.
        Uses prefetch_related and select_related to minimize database hits.
        """
        return self.filter(
            participants=user
        ).select_related().prefetch_related(
            'participants',
            Prefetch(
                'messages',
                queryset=ThreadedMessage.objects.select_related(
                    'sender', 'parent_message'
                ).order_by('timestamp')
            )
        ).annotate(
            message_count=Count('messages'),
            latest_activity=Max('messages__timestamp')
        ).order_by('-latest_activity')[:limit]
    
    def search_conversations(self, user, query):
        """Search conversations with content matching the query."""
        return self.filter(
            participants=user,
            messages__content__icontains=query
        ).distinct().select_related().prefetch_related(
            'participants',
            'messages__sender'
        )


class Conversation(models.Model):
    """
    Model representing a conversation thread between multiple users.
    
    This model acts as a container for threaded messages and helps
    optimize queries by grouping related messages together.
    """
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title for the conversation"
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text="Users participating in this conversation"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the conversation was started"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the conversation was last updated"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Whether the conversation is archived"
    )
    
    objects = ConversationManager()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
    
    def __str__(self):
        participant_names = ", ".join([u.username for u in self.participants.all()[:3]])
        if self.participants.count() > 3:
            participant_names += f" +{self.participants.count() - 3} more"
        return f"Conversation: {participant_names}"
    
    def get_root_messages(self):
        """Get all root messages in this conversation."""
        return self.messages.filter(parent_message__isnull=True).order_by('timestamp')
    
    def get_message_count(self):
        """Get total number of messages in this conversation."""
        return self.messages.count()
    
    def get_latest_message(self):
        """Get the most recent message in this conversation."""
        return self.messages.order_by('-timestamp').first()
    
    def add_participant(self, user):
        """Add a user to the conversation."""
        self.participants.add(user)
        self.save()
    
    def remove_participant(self, user):
        """Remove a user from the conversation."""
        self.participants.remove(user)
        self.save()


class ThreadedMessageManager(models.Manager):
    """Custom manager for optimized threaded message queries."""
    
    def get_conversation_tree(self, conversation_id):
        """
        Get all messages in a conversation organized as a tree structure.
        Uses optimized queries with select_related and prefetch_related.
        """
        messages = self.filter(
            conversation_id=conversation_id
        ).select_related(
            'sender', 'parent_message', 'conversation'
        ).prefetch_related(
            'replies__sender',
            'history'
        ).order_by('timestamp')
        
        # Build tree structure
        message_dict = {}
        root_messages = []
        
        for message in messages:
            message_dict[message.id] = message
            message.children = []
            
            if message.parent_message_id is None:
                root_messages.append(message)
            else:
                parent = message_dict.get(message.parent_message_id)
                if parent:
                    parent.children.append(message)
        
        return root_messages
    
    def get_thread_messages(self, root_message_id, max_depth=10):
        """
        Get all messages in a thread starting from a root message.
        Uses recursive CTE for PostgreSQL or manual recursion for other databases.
        """
        from django.db import connection
        
        if 'postgresql' in connection.vendor:
            # Use PostgreSQL's recursive CTE for optimal performance
            return self.raw("""
                WITH RECURSIVE thread_messages AS (
                    -- Base case: root message
                    SELECT id, sender_id, parent_message_id, content, timestamp, thread_level, 0 as depth
                    FROM messaging_threadedmessage 
                    WHERE id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: replies
                    SELECT m.id, m.sender_id, m.parent_message_id, m.content, m.timestamp, m.thread_level, tm.depth + 1
                    FROM messaging_threadedmessage m
                    JOIN thread_messages tm ON m.parent_message_id = tm.id
                    WHERE tm.depth < %s
                )
                SELECT * FROM thread_messages ORDER BY timestamp
            """, [root_message_id, max_depth])
        else:
            # Fallback for other databases
            def get_replies(message_id, current_depth=0):
                if current_depth >= max_depth:
                    return []
                
                replies = list(self.filter(parent_message_id=message_id).select_related('sender'))
                all_replies = replies[:]
                
                for reply in replies:
                    all_replies.extend(get_replies(reply.id, current_depth + 1))
                
                return all_replies
            
            root_message = self.select_related('sender').get(id=root_message_id)
            thread_messages = [root_message] + get_replies(root_message_id)
            return sorted(thread_messages, key=lambda x: x.timestamp)


class ThreadedMessage(models.Model):
    """
    Enhanced message model with threaded conversation support.
    
    This model extends the basic message functionality with threading
    capabilities and optimized querying methods.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The conversation this message belongs to"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='threaded_sent_messages',
        help_text="The user who sent this message"
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="The message this is a reply to"
    )
    content = models.TextField(
        max_length=2000,
        help_text="The message content"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the message was created"
    )
    thread_level = models.PositiveIntegerField(
        default=0,
        help_text="The depth level in the conversation thread"
    )
    is_read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name='read_threaded_messages',
        help_text="Users who have read this message"
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
    
    objects = ThreadedMessageManager()
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Threaded Message"
        verbose_name_plural = "Threaded Messages"
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['parent_message', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
        ]
    
    def __str__(self):
        prefix = "Reply: " if self.parent_message else "Root: "
        return f"{prefix}{self.content[:50]}... by {self.sender.username}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set thread_level and update conversation."""
        if self.parent_message:
            self.thread_level = self.parent_message.thread_level + 1
        else:
            self.thread_level = 0
        
        super().save(*args, **kwargs)
        
        # Update conversation timestamp
        if self.conversation:
            self.conversation.updated_at = timezone.now()
            self.conversation.save(update_fields=['updated_at'])
    
    def is_root_message(self):
        """Check if this is a root message in the thread."""
        return self.parent_message is None
    
    def get_root_message(self):
        """Get the root message of this thread."""
        if self.is_root_message():
            return self
        
        current = self
        while current.parent_message:
            current = current.parent_message
        return current
    
    def get_reply_count(self):
        """Get the total number of replies to this message."""
        return self.replies.count()
    
    def get_thread_participants(self):
        """Get all users who have participated in this message thread."""
        root = self.get_root_message()
        thread_messages = ThreadedMessage.objects.get_thread_messages(root.id)
        
        participant_ids = set()
        for message in thread_messages:
            participant_ids.add(message.sender_id)
        
        return User.objects.filter(id__in=participant_ids)
    
    def mark_as_read(self, user):
        """Mark this message as read by a specific user."""
        self.is_read_by.add(user)
    
    def is_read_by_user(self, user):
        """Check if this message has been read by a specific user."""
        return self.is_read_by.filter(id=user.id).exists()
    
    def get_unread_count_for_user(self, user):
        """Get count of unread replies for a specific user."""
        return self.replies.exclude(is_read_by=user).count()


class MessageReaction(models.Model):
    """
    Model for message reactions/emotions (like, dislike, love, etc.).
    
    This allows users to react to messages in threaded conversations.
    """
    REACTION_CHOICES = [
        ('👍', 'Like'),
        ('👎', 'Dislike'),
        ('❤️', 'Love'),
        ('😂', 'Laugh'),
        ('😮', 'Surprise'),
        ('😢', 'Sad'),
        ('😡', 'Angry'),
    ]
    
    message = models.ForeignKey(
        ThreadedMessage,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    reaction = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES,
        help_text="The type of reaction"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the reaction was added"
    )
    
    class Meta:
        unique_together = ['message', 'user', 'reaction']
        verbose_name = "Message Reaction"
        verbose_name_plural = "Message Reactions"
    
    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to message #{self.message.id}"


class ConversationMembership(models.Model):
    """
    Model to track user membership in conversations with additional metadata.
    
    This provides more control over conversation participation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_memberships'
    )
    joined_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the user joined the conversation"
    )
    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user last read messages in this conversation"
    )
    is_muted = models.BooleanField(
        default=False,
        help_text="Whether the user has muted notifications for this conversation"
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Administrator'),
            ('moderator', 'Moderator'),
            ('member', 'Member'),
        ],
        default='member',
        help_text="User's role in the conversation"
    )
    
    class Meta:
        unique_together = ['conversation', 'user']
        verbose_name = "Conversation Membership"
        verbose_name_plural = "Conversation Memberships"
    
    def __str__(self):
        return f"{self.user.username} in {self.conversation}"
    
    def get_unread_count(self):
        """Get the number of unread messages for this user in this conversation."""
        if not self.last_read_at:
            return self.conversation.messages.count()
        
        return self.conversation.messages.filter(
            timestamp__gt=self.last_read_at
        ).exclude(sender=self.user).count()
    
    def mark_as_read(self):
        """Mark all messages in the conversation as read for this user."""
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])
