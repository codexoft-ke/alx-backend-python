"""
Advanced ORM managers and querysets for threaded conversations.

This module provides optimized database queries using Django's advanced
ORM features like select_related, prefetch_related, and custom querysets.
"""
from django.db import models
from django.db.models import Q, Count, Max, Min, Avg, Prefetch, Case, When, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.utils import timezone


class OptimizedConversationQuerySet(models.QuerySet):
    """Custom queryset with optimized methods for conversation queries."""
    
    def with_message_counts(self):
        """Annotate conversations with message counts."""
        return self.annotate(
            total_messages=Count('messages'),
            root_messages=Count('messages', filter=Q(messages__parent_message__isnull=True)),
            reply_messages=Count('messages', filter=Q(messages__parent_message__isnull=False))
        )
    
    def with_latest_activity(self):
        """Annotate conversations with latest activity timestamps."""
        return self.annotate(
            latest_message_time=Max('messages__timestamp'),
            first_message_time=Min('messages__timestamp')
        )
    
    def with_participant_info(self):
        """Annotate conversations with participant information."""
        return self.annotate(
            participant_count=Count('participants', distinct=True)
        )
    
    def for_user(self, user):
        """Filter conversations that include the specified user."""
        return self.filter(participants=user)
    
    def active_conversations(self):
        """Filter to only active (non-archived) conversations."""
        return self.filter(is_archived=False)
    
    def with_full_optimization(self):
        """Apply all optimizations for comprehensive conversation loading."""
        return self.select_related().prefetch_related(
            'participants',
            Prefetch(
                'messages',
                queryset=models.Model.objects.select_related(
                    'sender', 'parent_message'
                ).prefetch_related('replies', 'reactions')
            ),
            'memberships__user'
        ).with_message_counts().with_latest_activity().with_participant_info()


class OptimizedMessageQuerySet(models.QuerySet):
    """Custom queryset with optimized methods for message queries."""
    
    def root_messages(self):
        """Filter to only root messages (not replies)."""
        return self.filter(parent_message__isnull=True)
    
    def replies(self):
        """Filter to only reply messages."""
        return self.filter(parent_message__isnull=False)
    
    def in_conversation(self, conversation):
        """Filter messages in a specific conversation."""
        return self.filter(conversation=conversation)
    
    def by_user(self, user):
        """Filter messages sent by a specific user."""
        return self.filter(sender=user)
    
    def unread_for_user(self, user):
        """Filter messages that are unread by a specific user."""
        return self.exclude(is_read_by=user)
    
    def with_reply_counts(self):
        """Annotate messages with their reply counts."""
        return self.annotate(
            direct_replies=Count('replies'),
            total_replies=Count('replies') + Count('replies__replies')  # Simplified 2-level count
        )
    
    def with_reaction_counts(self):
        """Annotate messages with reaction counts."""
        return self.annotate(
            total_reactions=Count('reactions'),
            like_count=Count('reactions', filter=Q(reactions__reaction='👍')),
            love_count=Count('reactions', filter=Q(reactions__reaction='❤️')),
            laugh_count=Count('reactions', filter=Q(reactions__reaction='😂'))
        )
    
    def with_read_status(self, user):
        """Annotate messages with read status for a specific user."""
        return self.annotate(
            is_read=Case(
                When(is_read_by=user, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            )
        )
    
    def thread_optimized(self):
        """Apply optimizations specifically for threaded display."""
        return self.select_related(
            'sender', 'conversation', 'parent_message', 'parent_message__sender'
        ).prefetch_related(
            'replies__sender',
            'reactions__user',
            'is_read_by'
        ).with_reply_counts().with_reaction_counts()
    
    def search_content(self, query):
        """Search messages by content with case-insensitive matching."""
        return self.filter(
            Q(content__icontains=query)
        )
    
    def recent_messages(self, days=7):
        """Filter messages from the last N days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(timestamp__gte=cutoff_date)


class ConversationTreeBuilder:
    """
    Utility class for building optimized conversation trees.
    
    This class provides methods to efficiently construct threaded
    conversation structures from database queries.
    """
    
    @staticmethod
    def build_thread_tree(messages):
        """
        Build a hierarchical tree structure from a flat list of messages.
        
        Args:
            messages: QuerySet or list of messages
            
        Returns:
            list: Root messages with nested replies
        """
        message_dict = {}
        root_messages = []
        
        # First pass: index all messages and initialize children lists
        for message in messages:
            message_dict[message.id] = message
            message.children = []
            message.depth = getattr(message, 'thread_level', 0)
        
        # Second pass: build parent-child relationships
        for message in messages:
            if message.parent_message_id is None:
                root_messages.append(message)
            else:
                parent = message_dict.get(message.parent_message_id)
                if parent:
                    parent.children.append(message)
        
        return root_messages
    
    @staticmethod
    def flatten_thread_tree(root_messages, max_depth=10):
        """
        Flatten a hierarchical tree back to a list with depth indicators.
        
        Args:
            root_messages: List of root messages with children
            max_depth: Maximum depth to traverse
            
        Returns:
            list: Flattened messages with depth information
        """
        flattened = []
        
        def traverse(messages, depth=0):
            if depth > max_depth:
                return
            
            for message in messages:
                message.display_depth = depth
                flattened.append(message)
                if hasattr(message, 'children') and message.children:
                    traverse(message.children, depth + 1)
        
        traverse(root_messages)
        return flattened
    
    @staticmethod
    def get_thread_statistics(messages):
        """
        Calculate statistics for a conversation thread.
        
        Args:
            messages: List or QuerySet of messages
            
        Returns:
            dict: Thread statistics
        """
        if not messages:
            return {}
        
        participants = set()
        total_messages = len(messages)
        root_count = 0
        max_depth = 0
        total_length = 0
        
        for message in messages:
            participants.add(message.sender_id)
            total_length += len(message.content)
            
            if not hasattr(message, 'parent_message_id') or message.parent_message_id is None:
                root_count += 1
            
            depth = getattr(message, 'thread_level', 0)
            max_depth = max(max_depth, depth)
        
        return {
            'total_messages': total_messages,
            'root_messages': root_count,
            'reply_messages': total_messages - root_count,
            'unique_participants': len(participants),
            'max_thread_depth': max_depth,
            'average_message_length': total_length // total_messages if total_messages > 0 else 0,
            'total_content_length': total_length
        }


class ConversationAnalytics:
    """
    Advanced analytics for conversation patterns and user engagement.
    """
    
    @staticmethod
    def get_user_conversation_stats(user, days=30):
        """
        Get comprehensive conversation statistics for a user.
        
        Args:
            user: User object
            days: Number of days to analyze
            
        Returns:
            dict: User conversation statistics
        """
        from .threaded_models import Conversation, ThreadedMessage
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Get user's conversations and messages
        conversations = Conversation.objects.filter(
            participants=user,
            updated_at__gte=cutoff_date
        )
        
        sent_messages = ThreadedMessage.objects.filter(
            sender=user,
            timestamp__gte=cutoff_date
        )
        
        received_messages = ThreadedMessage.objects.filter(
            conversation__participants=user,
            timestamp__gte=cutoff_date
        ).exclude(sender=user)
        
        return {
            'active_conversations': conversations.count(),
            'messages_sent': sent_messages.count(),
            'messages_received': received_messages.count(),
            'root_messages_started': sent_messages.filter(parent_message__isnull=True).count(),
            'replies_sent': sent_messages.filter(parent_message__isnull=False).count(),
            'average_message_length': sent_messages.aggregate(
                avg_len=Avg(models.functions.Length('content'))
            )['avg_len'] or 0,
            'most_active_conversation': conversations.annotate(
                user_message_count=Count('messages', filter=Q(messages__sender=user))
            ).order_by('-user_message_count').first(),
            'conversation_initiation_rate': (
                sent_messages.filter(parent_message__isnull=True).count() /
                max(conversations.count(), 1)
            )
        }
    
    @staticmethod
    def get_conversation_engagement_metrics(conversation):
        """
        Calculate engagement metrics for a specific conversation.
        
        Args:
            conversation: Conversation object
            
        Returns:
            dict: Engagement metrics
        """
        from .threaded_models import ThreadedMessage
        
        messages = ThreadedMessage.objects.filter(conversation=conversation)
        
        if not messages.exists():
            return {}
        
        # Calculate various engagement metrics
        participant_message_counts = messages.values('sender').annotate(
            message_count=Count('id')
        ).order_by('-message_count')
        
        thread_depths = messages.aggregate(
            max_depth=Max('thread_level'),
            avg_depth=Avg('thread_level')
        )
        
        response_times = []
        root_messages = messages.filter(parent_message__isnull=True)
        
        for root in root_messages:
            first_reply = messages.filter(parent_message=root).first()
            if first_reply:
                response_time = (first_reply.timestamp - root.timestamp).total_seconds()
                response_times.append(response_time)
        
        return {
            'total_messages': messages.count(),
            'unique_participants': messages.values('sender').distinct().count(),
            'most_active_participant': participant_message_counts.first() if participant_message_counts else None,
            'participation_balance': (
                min([p['message_count'] for p in participant_message_counts]) /
                max([p['message_count'] for p in participant_message_counts])
                if len(participant_message_counts) > 1 else 1.0
            ),
            'max_thread_depth': thread_depths['max_depth'] or 0,
            'average_thread_depth': round(thread_depths['avg_depth'] or 0, 2),
            'average_response_time_seconds': (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            'thread_initiation_count': root_messages.count(),
            'conversation_duration_hours': (
                (messages.aggregate(Max('timestamp'))['timestamp__max'] -
                 messages.aggregate(Min('timestamp'))['timestamp__min']).total_seconds() / 3600
                if messages.count() > 1 else 0
            )
        }


class AdvancedSearchManager:
    """
    Advanced search functionality for threaded conversations.
    """
    
    @staticmethod
    def search_conversations(user, query, search_type='content'):
        """
        Advanced search across user's conversations.
        
        Args:
            user: User object
            query: Search query string
            search_type: Type of search ('content', 'participant', 'both')
            
        Returns:
            QuerySet: Matching conversations with highlighted results
        """
        from .threaded_models import Conversation, ThreadedMessage
        
        base_conversations = Conversation.objects.filter(participants=user)
        
        if search_type == 'content':
            # Search in message content
            matching_conversations = base_conversations.filter(
                messages__content__icontains=query
            ).distinct()
            
        elif search_type == 'participant':
            # Search by participant username
            matching_conversations = base_conversations.filter(
                participants__username__icontains=query
            ).distinct()
            
        else:  # search_type == 'both'
            # Search both content and participants
            matching_conversations = base_conversations.filter(
                Q(messages__content__icontains=query) |
                Q(participants__username__icontains=query)
            ).distinct()
        
        # Add search context
        return matching_conversations.prefetch_related(
            Prefetch(
                'messages',
                queryset=ThreadedMessage.objects.filter(
                    content__icontains=query
                ).select_related('sender'),
                to_attr='matching_messages'
            )
        ).with_full_optimization()
    
    @staticmethod
    def get_search_suggestions(user, partial_query, limit=10):
        """
        Get search suggestions based on user's conversation history.
        
        Args:
            user: User object
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            list: Search suggestions
        """
        from .threaded_models import ThreadedMessage
        
        # Get frequently used words from user's messages
        user_messages = ThreadedMessage.objects.filter(
            conversation__participants=user
        ).values_list('content', flat=True)
        
        # Simple word frequency analysis (in a real app, you'd use more sophisticated NLP)
        suggestions = []
        for content in user_messages:
            words = content.lower().split()
            for word in words:
                if (len(word) > 3 and 
                    word.startswith(partial_query.lower()) and 
                    word not in suggestions):
                    suggestions.append(word)
                    if len(suggestions) >= limit:
                        break
            if len(suggestions) >= limit:
                break
        
        return suggestions[:limit]
