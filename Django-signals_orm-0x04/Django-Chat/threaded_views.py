"""
Advanced views for threaded conversations with optimized ORM queries.

This module demonstrates the use of select_related, prefetch_related,
and custom querysets for efficient threaded conversation handling.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Prefetch, Q, Count, Max
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User

# Import our enhanced models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from messaging.models import Message, MessageHistory


class ThreadedConversationListView(LoginRequiredMixin, ListView):
    """
    View to list threaded conversations with optimized queries.
    
    Uses select_related and prefetch_related to minimize database hits.
    """
    template_name = 'messaging/threaded_conversations.html'
    context_object_name = 'conversations'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Get conversations with optimized queries.
        
        Uses Message.get_threaded_conversations() for efficient loading
        of conversation threads with minimal database queries.
        """
        user = self.request.user
        
        # Get root messages (conversations) with optimized prefetching
        conversations = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            # Prefetch direct replies with their senders
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
            ),
            # Prefetch message history
            'history',
            # Prefetch notifications
            'notifications'
        ).annotate(
            # Annotate with reply count
            reply_count=Count('replies'),
            # Annotate with latest activity
            latest_reply=Max('replies__timestamp')
        ).order_by('-timestamp')
        
        return conversations
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        
        # Add conversation statistics
        user = self.request.user
        context['conversation_stats'] = {
            'total_conversations': Message.objects.filter(
                Q(sender=user) | Q(receiver=user),
                parent_message__isnull=True
            ).count(),
            'unread_conversations': Message.objects.filter(
                receiver=user,
                parent_message__isnull=True,
                is_read=False
            ).count(),
            'active_threads': Message.objects.filter(
                Q(sender=user) | Q(receiver=user),
                parent_message__isnull=True,
                replies__timestamp__gte=timezone.now() - timezone.timedelta(days=7)
            ).distinct().count()
        }
        
        return context


class ThreadedConversationDetailView(LoginRequiredMixin, DetailView):
    """
    View to display a complete threaded conversation.
    
    Uses recursive queries and prefetch_related for efficient
    loading of the entire conversation tree.
    """
    model = Message
    template_name = 'messaging/threaded_conversation_detail.html'
    context_object_name = 'root_message'
    
    def get_object(self):
        """Get the root message and verify user permissions."""
        message = get_object_or_404(Message, pk=self.kwargs['pk'])
        
        # Get the root message if this is a reply
        root_message = message.get_root_message()
        
        # Check if user has permission to view this conversation
        user = self.request.user
        if (root_message.sender != user and root_message.receiver != user and
            not root_message.get_all_replies().filter(
                Q(sender=user) | Q(receiver=user)
            ).exists()):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this conversation.")
        
        return root_message
    
    def get_context_data(self, **kwargs):
        """
        Build the complete conversation thread with optimized queries.
        """
        context = super().get_context_data(**kwargs)
        root_message = self.object
        
        # Get all messages in the thread with optimized prefetching
        thread_messages = self.get_thread_messages(root_message)
        
        # Build the threaded structure
        conversation_tree = self.build_conversation_tree(thread_messages)
        
        context.update({
            'conversation_tree': conversation_tree,
            'thread_messages': thread_messages,
            'participants': self.get_thread_participants(thread_messages),
            'thread_stats': self.get_thread_statistics(thread_messages),
            'user_can_reply': self.user_can_reply(root_message),
        })
        
        return context
    
    def get_thread_messages(self, root_message):
        """
        Get all messages in the thread with optimized queries.
        
        Uses recursive querying to get all replies at any depth level.
        """
        # Start with the root message
        all_message_ids = {root_message.id}
        
        # Recursively collect all reply IDs
        def collect_reply_ids(message_ids, collected_ids, max_depth=10, current_depth=0):
            if current_depth >= max_depth or not message_ids:
                return collected_ids
            
            # Get direct replies to current message set
            reply_ids = set(
                Message.objects.filter(
                    parent_message_id__in=message_ids
                ).values_list('id', flat=True)
            )
            
            # Add new replies to collected set
            new_replies = reply_ids - collected_ids
            collected_ids.update(new_replies)
            
            # Recursively get replies to these replies
            if new_replies:
                collect_reply_ids(new_replies, collected_ids, max_depth, current_depth + 1)
            
            return collected_ids
        
        # Collect all message IDs in the thread
        collect_reply_ids({root_message.id}, all_message_ids)
        
        # Fetch all messages with optimized queries
        thread_messages = Message.objects.filter(
            id__in=all_message_ids
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            'history__edited_by',
            'notifications',
            'replies'  # This will be used for building the tree
        ).order_by('timestamp')
        
        return list(thread_messages)
    
    def build_conversation_tree(self, messages):
        """
        Build a hierarchical tree structure from flat message list.
        
        This creates a nested structure for template rendering.
        """
        message_dict = {}
        root_messages = []
        
        # Index messages and initialize children lists
        for message in messages:
            message_dict[message.id] = message
            message.children = []
            message.depth = 0
        
        # Build parent-child relationships and calculate depths
        for message in messages:
            if message.parent_message_id is None:
                root_messages.append(message)
            else:
                parent = message_dict.get(message.parent_message_id)
                if parent:
                    parent.children.append(message)
                    message.depth = parent.depth + 1
        
        # Sort children by timestamp
        def sort_children(msg):
            msg.children.sort(key=lambda x: x.timestamp)
            for child in msg.children:
                sort_children(child)
        
        for root in root_messages:
            sort_children(root)
        
        return root_messages
    
    def get_thread_participants(self, messages):
        """Get all users who have participated in the thread."""
        participant_ids = set()
        for message in messages:
            participant_ids.add(message.sender_id)
            if hasattr(message, 'receiver_id'):
                participant_ids.add(message.receiver_id)
        
        return User.objects.filter(
            id__in=participant_ids
        ).select_related('profile')
    
    def get_thread_statistics(self, messages):
        """Calculate statistics for the conversation thread."""
        if not messages:
            return {}
        
        root_count = sum(1 for msg in messages if not msg.parent_message_id)
        reply_count = len(messages) - root_count
        max_depth = max((getattr(msg, 'depth', 0) for msg in messages), default=0)
        
        # Calculate average response time
        response_times = []
        for message in messages:
            if message.parent_message_id:
                parent = next((m for m in messages if m.id == message.parent_message_id), None)
                if parent:
                    response_time = (message.timestamp - parent.timestamp).total_seconds()
                    response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_messages': len(messages),
            'root_messages': root_count,
            'replies': reply_count,
            'max_depth': max_depth,
            'unique_participants': len(set(msg.sender_id for msg in messages)),
            'average_response_time_minutes': round(avg_response_time / 60, 1),
            'conversation_duration_hours': round(
                (messages[-1].timestamp - messages[0].timestamp).total_seconds() / 3600, 1
            ) if len(messages) > 1 else 0
        }
    
    def user_can_reply(self, root_message):
        """Check if the current user can reply to this conversation."""
        user = self.request.user
        return (user == root_message.sender or 
                user == root_message.receiver or
                root_message.get_all_replies().filter(
                    Q(sender=user) | Q(receiver=user)
                ).exists())


@login_required
def send_threaded_reply(request, parent_id):
    """
    View to send a reply to a specific message in a thread.
    
    Handles the creation of threaded replies with proper parent-child relationships.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    parent_message = get_object_or_404(Message, id=parent_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)
    
    # Check if user can reply to this thread
    user = request.user
    root_message = parent_message.get_root_message()
    
    if not (user == root_message.sender or user == root_message.receiver or
            root_message.get_all_replies().filter(Q(sender=user) | Q(receiver=user)).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Determine the receiver (original conversation participants)
    if parent_message.sender == user:
        receiver = parent_message.receiver
    else:
        receiver = parent_message.sender
    
    # Create the reply message
    reply = Message.objects.create(
        sender=user,
        receiver=receiver,
        content=content,
        parent_message=parent_message
    )
    
    return JsonResponse({
        'success': True,
        'message_id': reply.id,
        'content': reply.content,
        'sender': reply.sender.username,
        'timestamp': reply.timestamp.isoformat(),
        'thread_level': reply.thread_level
    })


@login_required
def conversation_search(request):
    """
    Advanced search functionality for threaded conversations.
    
    Uses optimized queries to search across message content and participants.
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'content')  # content, participants, or both
    
    if not query:
        return render(request, 'messaging/conversation_search.html', {
            'query': query,
            'results': [],
            'search_type': search_type
        })
    
    user = request.user
    
    # Build search query based on type
    if search_type == 'content':
        # Search in message content
        matching_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            content__icontains=query
        ).select_related('sender', 'receiver', 'parent_message')
        
    elif search_type == 'participants':
        # Search by participant usernames
        matching_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            Q(sender__username__icontains=query) | Q(receiver__username__icontains=query)
        ).select_related('sender', 'receiver', 'parent_message')
        
    else:  # both
        # Search both content and participants
        matching_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            Q(content__icontains=query) |
            Q(sender__username__icontains=query) |
            Q(receiver__username__icontains=query)
        ).select_related('sender', 'receiver', 'parent_message')
    
    # Group results by conversation thread
    conversations = {}
    for message in matching_messages.order_by('-timestamp')[:100]:  # Limit results
        root = message.get_root_message()
        if root.id not in conversations:
            conversations[root.id] = {
                'root_message': root,
                'matching_messages': [],
                'total_messages': root.get_reply_count() + 1
            }
        conversations[root.id]['matching_messages'].append(message)
    
    # Convert to list and sort by latest activity
    results = list(conversations.values())
    results.sort(key=lambda x: max(
        msg.timestamp for msg in x['matching_messages']
    ), reverse=True)
    
    # Paginate results
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/conversation_search.html', {
        'query': query,
        'search_type': search_type,
        'results': page_obj,
        'total_results': len(results)
    })


@login_required
def conversation_analytics_api(request, message_id):
    """
    API endpoint to get analytics for a specific conversation thread.
    
    Returns engagement metrics, participant statistics, and thread analysis.
    """
    root_message = get_object_or_404(Message, id=message_id)
    
    # Verify user permission
    user = request.user
    if not (user == root_message.sender or user == root_message.receiver or
            root_message.get_all_replies().filter(Q(sender=user) | Q(receiver=user)).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get all thread messages with optimized query
    thread_messages = [root_message] + list(root_message.get_all_replies())
    
    # Calculate analytics
    participants = {}
    response_times = []
    message_lengths = []
    hourly_activity = {}
    
    for message in thread_messages:
        # Participant statistics
        sender_id = message.sender_id
        if sender_id not in participants:
            participants[sender_id] = {
                'username': message.sender.username,
                'message_count': 0,
                'total_length': 0,
                'replies_count': 0
            }
        
        participants[sender_id]['message_count'] += 1
        participants[sender_id]['total_length'] += len(message.content)
        message_lengths.append(len(message.content))
        
        if message.parent_message_id:
            participants[sender_id]['replies_count'] += 1
            
            # Calculate response time
            parent = next((m for m in thread_messages if m.id == message.parent_message_id), None)
            if parent:
                response_time = (message.timestamp - parent.timestamp).total_seconds()
                response_times.append(response_time)
        
        # Hourly activity
        hour_key = message.timestamp.strftime('%Y-%m-%d %H:00')
        hourly_activity[hour_key] = hourly_activity.get(hour_key, 0) + 1
    
    analytics_data = {
        'conversation_id': root_message.id,
        'total_messages': len(thread_messages),
        'unique_participants': len(participants),
        'participant_stats': list(participants.values()),
        'average_message_length': sum(message_lengths) / len(message_lengths) if message_lengths else 0,
        'average_response_time_minutes': sum(response_times) / len(response_times) / 60 if response_times else 0,
        'conversation_duration_hours': (
            (thread_messages[-1].timestamp - thread_messages[0].timestamp).total_seconds() / 3600
            if len(thread_messages) > 1 else 0
        ),
        'hourly_activity': hourly_activity,
        'engagement_score': min(len(thread_messages) * len(participants) / 10, 100)  # Simple engagement score
    }
    
    return JsonResponse(analytics_data)


class OptimizedConversationListView(LoginRequiredMixin, ListView):
    """
    Highly optimized conversation list view demonstrating advanced ORM techniques.
    
    This view showcases the use of select_related, prefetch_related, annotations,
    and custom querysets for maximum performance.
    """
    template_name = 'messaging/optimized_conversations.html'
    context_object_name = 'conversations'
    paginate_by = 25
    
    def get_queryset(self):
        """
        Get conversations with maximum optimization.
        
        This query demonstrates advanced ORM techniques:
        - select_related for foreign keys
        - prefetch_related for reverse foreign keys and many-to-many
        - annotations for calculated fields
        - conditional expressions
        - subqueries for complex calculations
        """
        from django.db.models import OuterRef, Subquery, Case, When, IntegerField
        
        user = self.request.user
        
        # Subquery to get the latest reply timestamp for each conversation
        latest_reply_subquery = Message.objects.filter(
            parent_message=OuterRef('pk')
        ).order_by('-timestamp').values('timestamp')[:1]
        
        # Subquery to get unread reply count
        unread_replies_subquery = Message.objects.filter(
            parent_message=OuterRef('pk'),
            receiver=user,
            is_read=False
        ).aggregate(count=Count('id'))['count']
        
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True  # Root messages only
        ).select_related(
            'sender',
            'sender__profile',  # Assuming UserProfile exists
            'receiver',
            'receiver__profile'
        ).prefetch_related(
            # Prefetch replies with their senders (limited to recent ones)
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender').order_by('-timestamp')[:5],
                to_attr='recent_replies'
            ),
            # Prefetch message history
            Prefetch(
                'history',
                queryset=MessageHistory.objects.select_related('edited_by').order_by('-version')[:3],
                to_attr='recent_edits'
            )
        ).annotate(
            # Count total replies
            reply_count=Count('replies'),
            
            # Count unread replies for current user
            unread_count=Count(
                'replies',
                filter=Q(replies__receiver=user, replies__is_read=False)
            ),
            
            # Get latest activity (either original message or latest reply)
            latest_activity=Case(
                When(replies__isnull=False, then=Subquery(latest_reply_subquery)),
                default='timestamp',
                output_field=models.DateTimeField()
            ),
            
            # Calculate engagement score
            engagement_score=Case(
                When(reply_count=0, then=1),
                When(reply_count__lt=5, then=reply_count * 2),
                When(reply_count__lt=20, then=reply_count + 5),
                default=25,
                output_field=IntegerField()
            )
        ).order_by('-latest_activity')


from django.utils import timezone
import datetime
