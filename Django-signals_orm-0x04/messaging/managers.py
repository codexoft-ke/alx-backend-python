"""
Custom ORM managers for the messaging app.

This module contains custom managers that provide optimized queries
for common messaging operations, especially for unread messages.
"""
from django.db import models
from django.db.models import Q, Count, Max
from django.utils import timezone


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for filtering unread messages for specific users.
    
    This manager provides optimized queries for unread messages
    with proper use of .only() to retrieve only necessary fields.
    """
    
    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        
        Uses .only() to optimize the query by loading only necessary fields.
        
        Args:
            user: The User instance to get unread messages for
            
        Returns:
            QuerySet: Optimized queryset of unread messages
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id',
            'sender__username',
            'sender__first_name',
            'sender__last_name',
            'content',
            'timestamp',
            'is_read',
            'parent_message_id'
        ).order_by('-timestamp')
    
    def count_for_user(self, user):
        """
        Get count of unread messages for a user (optimized).
        
        Args:
            user: The User instance to count unread messages for
            
        Returns:
            int: Number of unread messages
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).count()
    
    def inbox_for_user(self, user, limit=20):
        """
        Get optimized inbox view for a user with only necessary fields.
        
        This method demonstrates the use of .only() for maximum performance
        when displaying message lists.
        
        Args:
            user: The User instance
            limit: Maximum number of messages to return
            
        Returns:
            QuerySet: Highly optimized queryset for inbox display
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id',
            'sender__username',
            'content',
            'timestamp'
        ).order_by('-timestamp')[:limit]
    
    def mark_all_read_for_user(self, user):
        """
        Mark all unread messages as read for a specific user.
        
        Args:
            user: The User instance
            
        Returns:
            int: Number of messages marked as read
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )


class ReadMessagesManager(models.Manager):
    """
    Custom manager for filtering read messages.
    """
    
    def for_user(self, user):
        """
        Get all read messages for a specific user.
        
        Args:
            user: The User instance
            
        Returns:
            QuerySet: Read messages for the user
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=True
        ).select_related('sender').only(
            'id',
            'sender__username',
            'content',
            'timestamp',
            'read_at'
        ).order_by('-read_at')


class ConversationManager(models.Manager):
    """
    Custom manager for handling conversation threads.
    """
    
    def for_user(self, user):
        """
        Get conversation threads (root messages) for a user.
        
        Args:
            user: The User instance
            
        Returns:
            QuerySet: Root messages of conversations involving the user
        """
        return self.get_queryset().filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True
        ).select_related('sender', 'receiver').order_by('-timestamp')
    
    def with_unread_count(self, user):
        """
        Get conversations with unread message counts for a user.
        
        Args:
            user: The User instance
            
        Returns:
            QuerySet: Conversations annotated with unread counts
        """
        return self.for_user(user).annotate(
            unread_count=Count(
                'replies',
                filter=Q(replies__receiver=user, replies__is_read=False)
            ),
            total_replies=Count('replies'),
            latest_activity=Max('replies__timestamp')
        )
    
    def active_for_user(self, user, days=7):
        """
        Get recently active conversations for a user.
        
        Args:
            user: The User instance
            days: Number of days to consider as "recent"
            
        Returns:
            QuerySet: Recently active conversations
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.with_unread_count(user).filter(
            Q(timestamp__gte=cutoff_date) |
            Q(latest_activity__gte=cutoff_date)
        )


class OptimizedMessageManager(models.Manager):
    """
    Manager with various optimization techniques for different use cases.
    """
    
    def inbox_summary(self, user):
        """
        Get inbox summary with counts and recent messages.
        
        Args:
            user: The User instance
            
        Returns:
            dict: Summary data including counts and recent messages
        """
        # Get counts efficiently
        total_messages = self.get_queryset().filter(receiver=user).count()
        unread_count = self.get_queryset().filter(receiver=user, is_read=False).count()
        
        # Get recent messages with minimal fields
        recent_messages = self.get_queryset().filter(
            receiver=user
        ).select_related('sender').only(
            'id', 'sender__username', 'content', 'timestamp', 'is_read'
        ).order_by('-timestamp')[:5]
        
        return {
            'total_messages': total_messages,
            'unread_count': unread_count,
            'read_count': total_messages - unread_count,
            'recent_messages': list(recent_messages)
        }
    
    def search_optimized(self, user, query):
        """
        Optimized search in user's messages.
        
        Args:
            user: The User instance
            query: Search query string
            
        Returns:
            QuerySet: Matching messages with optimized fields
        """
        return self.get_queryset().filter(
            Q(receiver=user) | Q(sender=user),
            content__icontains=query
        ).select_related('sender', 'receiver').only(
            'id',
            'sender__username',
            'receiver__username', 
            'content',
            'timestamp',
            'is_read'
        ).order_by('-timestamp')
    
    def bulk_operations_ready(self):
        """
        Get queryset optimized for bulk operations.
        
        Returns:
            QuerySet: Queryset ready for bulk updates/deletes
        """
        return self.get_queryset().only('id', 'is_read', 'read_at')
