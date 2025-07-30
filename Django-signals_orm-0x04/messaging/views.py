"""
Views for the messaging app with advanced ORM optimization.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Prefetch, Q, Count, Max, OuterRef, Subquery, Case, When
from django.db.models import IntegerField, DateTimeField
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Message, Notification, MessageHistory


class UnreadMessagesView(LoginRequiredMixin, ListView):
    """
    View to display only unread messages using the custom UnreadMessagesManager.
    
    Demonstrates the use of custom managers with .only() optimization.
    """
    template_name = 'messaging/unread_messages.html'
    context_object_name = 'unread_messages'
    paginate_by = 25

    def get_queryset(self):
        """
        Get unread messages using the custom manager with optimized queries.
        
        Uses the UnreadMessagesManager to get only unread messages
        and .only() to retrieve minimal fields for performance.
        """
        # Use the custom unread manager with the specific method name
        return Message.unread.unread_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        """Add unread message statistics to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Use custom managers for statistics
        context['inbox_stats'] = Message.get_inbox_summary(user)
        context['recent_conversations'] = Message.conversations.for_user(user)[:5]
        
        return context


class OptimizedInboxView(LoginRequiredMixin, ListView):
    """
    Highly optimized inbox view using custom managers and .only() fields.
    
    Demonstrates advanced ORM optimization techniques with custom managers.
    """
    template_name = 'messaging/optimized_inbox.html'
    context_object_name = 'messages'
    paginate_by = 30

    def get_queryset(self):
        """
        Get inbox messages with maximum optimization.
        
        Uses custom managers and .only() to retrieve minimal fields,
        reducing database load and memory usage.
        """
        user = self.request.user
        
        # Use the custom unread manager for optimized inbox display
        return Message.unread.inbox_for_user(user, limit=100)

    def get_context_data(self, **kwargs):
        """Add comprehensive inbox context with custom manager data."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get statistics using custom managers
        context.update({
            'unread_count': Message.unread.count_for_user(user),
            'conversation_threads': Message.conversations.with_unread_count(user)[:10],
            'inbox_summary': Message.get_inbox_summary(user),
            'recent_activity': self.get_recent_activity(user)
        })
        
        return context

    def get_recent_activity(self, user):
        """Get recent activity using optimized queries."""
        return {
            'recent_sent': Message.objects.filter(sender=user).only(
                'id', 'receiver__username', 'content', 'timestamp', 'is_read'
            ).select_related('receiver')[:5],
            'recent_received': Message.objects.filter(receiver=user).only(
                'id', 'sender__username', 'content', 'timestamp', 'is_read'
            ).select_related('sender')[:5]
        }


@login_required
def mark_messages_as_read(request):
    """
    API endpoint to mark messages as read using custom manager methods.
    
    Demonstrates bulk operations with custom managers.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    user = request.user
    message_ids = request.POST.getlist('message_ids[]')
    
    if not message_ids:
        # Mark all unread messages as read
        updated_count = Message.objects.filter(
            receiver=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
    else:
        # Mark specific messages as read
        updated_count = Message.objects.filter(
            id__in=message_ids,
            receiver=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    # Get updated statistics using custom managers
    stats = Message.get_inbox_summary(user)
    
    return JsonResponse({
        'success': True,
        'updated_count': updated_count,
        'new_unread_count': stats['unread_count'],
        'stats': stats
    })


@login_required
def unread_messages_api(request):
    """
    API endpoint to get unread messages using custom manager.
    
    Returns optimized unread message data using .only() fields.
    """
    user = request.user
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    
    # Use custom manager with optimization
    unread_messages = Message.unread.for_user(user)[offset:offset + limit]
    
    messages_data = []
    for message in unread_messages:
        messages_data.append({
            'id': message.id,
            'sender': message.sender.username,
            'content_preview': message.content[:100] + '...' if len(message.content) > 100 else message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_reply': message.parent_message_id is not None,
            'thread_level': message.thread_level
        })
    
    return JsonResponse({
        'messages': messages_data,
        'total_unread': Message.unread.count_for_user(user),
        'has_more': len(unread_messages) == limit
    })


@login_required
def conversation_unread_count_api(request, conversation_id):
    """
    API endpoint to get unread count for a specific conversation.
    
    Uses custom managers for efficient counting.
    """
    user = request.user
    
    try:
        root_message = Message.conversations.get(id=conversation_id)
        
        # Check if user has access to this conversation
        if not (root_message.sender == user or root_message.receiver == user):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Count unread messages in this conversation thread
        thread_messages = [root_message] + list(root_message.get_all_replies())
        unread_count = sum(
            1 for msg in thread_messages 
            if msg.receiver == user and not msg.is_read
        )
        
        return JsonResponse({
            'conversation_id': conversation_id,
            'unread_count': unread_count,
            'total_messages': len(thread_messages)
        })
        
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)


@login_required
def unread_inbox_view(request):
    """
    Simple function-based view demonstrating the use of custom managers.
    
    This view uses Message.unread.unread_for_user() to display only
    unread messages for the current user's inbox.
    """
    user = request.user
    
    # Use the custom UnreadMessagesManager to get unread messages
    unread_messages = Message.unread.unread_for_user(user)
    
    # Get additional statistics using other custom managers
    unread_count = Message.unread.count_for_user(user)
    recent_conversations = Message.conversations.for_user(user)[:5]
    
    # Get optimized inbox preview (limited fields)
    inbox_preview = Message.unread.inbox_for_user(user, limit=10)
    
    context = {
        'unread_messages': unread_messages,
        'unread_count': unread_count,
        'recent_conversations': recent_conversations,
        'inbox_preview': inbox_preview,
        'page_title': f'Unread Messages ({unread_count})'
    }
    
    return render(request, 'messaging/unread_inbox.html', context)


class MessageListView(LoginRequiredMixin, ListView):
    """
    View to list messages for the current user with optimized queries.
    
    Uses select_related and prefetch_related to minimize database hits.
    """
    model = Message
    template_name = 'messaging/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Return messages for the current user with optimized prefetching.
        
        Uses select_related for foreign keys and prefetch_related for
        reverse relationships to minimize database queries.
        """
        return Message.objects.filter(
            Q(receiver=self.request.user) | Q(sender=self.request.user)
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            # Prefetch replies with their senders for threaded conversations
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
            ),
            # Prefetch message history
            Prefetch(
                'history',
                queryset=MessageHistory.objects.select_related('edited_by').order_by('-version')
            ),
            # Prefetch notifications
            'notifications'
        ).annotate(
            # Count replies for each message
            reply_count=Count('replies'),
            # Get latest reply timestamp
            latest_reply=Max('replies__timestamp')
        ).order_by('-timestamp')


class SendMessageView(LoginRequiredMixin, CreateView):
    """
    View to send a new message or reply to an existing message.
    
    Handles both root messages and threaded replies.
    """
    model = Message
    fields = ['receiver', 'content', 'parent_message']
    template_name = 'messaging/send_message.html'
    success_url = reverse_lazy('messaging:message_list')

    def form_valid(self, form):
        """Set the sender to the current user and handle threading."""
        form.instance.sender = self.request.user
        
        # If this is a reply, set the thread level
        if form.instance.parent_message:
            form.instance.thread_level = form.instance.parent_message.thread_level + 1
        
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add parent message to context if replying."""
        context = super().get_context_data(**kwargs)
        parent_id = self.request.GET.get('reply_to')
        if parent_id:
            try:
                parent_message = Message.objects.select_related('sender', 'receiver').get(id=parent_id)
                context['parent_message'] = parent_message
                context['is_reply'] = True
            except Message.DoesNotExist:
                pass
        return context


class ThreadedConversationView(LoginRequiredMixin, DetailView):
    """
    View to display a complete threaded conversation with optimized queries.
    
    Uses recursive queries and advanced prefetching for efficient loading
    of the entire conversation tree.
    """
    model = Message
    template_name = 'messaging/threaded_conversation.html'
    context_object_name = 'root_message'

    def get_queryset(self):
        """Get messages with optimized prefetching."""
        return Message.objects.select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            'replies__sender',
            'replies__receiver', 
            'history__edited_by'
        )

    def get_object(self):
        """Get the root message and verify permissions."""
        message = super().get_object()
        
        # Get root message if this is a reply
        while message.parent_message:
            message = message.parent_message
        
        # Verify user has permission to view this conversation
        user = self.request.user
        if not (message.sender == user or message.receiver == user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this conversation.")
        
        return message

    def get_context_data(self, **kwargs):
        """Build the complete threaded conversation."""
        context = super().get_context_data(**kwargs)
        root_message = self.object
        
        # Get all messages in thread with optimized query
        thread_messages = self.get_thread_messages(root_message)
        
        # Build conversation tree
        conversation_tree = self.build_conversation_tree(thread_messages)
        
        context.update({
            'conversation_tree': conversation_tree,
            'thread_messages': thread_messages,
            'thread_stats': self.get_thread_stats(thread_messages),
            'can_reply': self.user_can_reply(root_message)
        })
        
        return context

    def get_thread_messages(self, root_message):
        """
        Get all messages in thread using recursive querying.
        
        Uses optimized queries with select_related and prefetch_related.
        """
        # Collect all message IDs in the thread
        message_ids = {root_message.id}
        
        def collect_replies(msg_ids, depth=0, max_depth=20):
            if depth >= max_depth:
                return
            
            reply_ids = set(Message.objects.filter(
                parent_message_id__in=msg_ids
            ).values_list('id', flat=True))
            
            if reply_ids:
                message_ids.update(reply_ids)
                collect_replies(reply_ids, depth + 1, max_depth)
        
        collect_replies({root_message.id})
        
        # Fetch all messages with optimized queries
        return Message.objects.filter(
            id__in=message_ids
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            Prefetch(
                'history',
                queryset=MessageHistory.objects.select_related('edited_by').order_by('-version')
            )
        ).order_by('timestamp')

    def build_conversation_tree(self, messages):
        """Build hierarchical tree structure from flat message list."""
        message_dict = {msg.id: msg for msg in messages}
        
        for message in messages:
            message.children = []
            message.depth = 0
        
        root_messages = []
        for message in messages:
            if message.parent_message_id is None:
                root_messages.append(message)
            else:
                parent = message_dict.get(message.parent_message_id)
                if parent:
                    parent.children.append(message)
                    message.depth = parent.depth + 1
        
        return root_messages

    def get_thread_stats(self, messages):
        """Calculate thread statistics."""
        return {
            'total_messages': len(messages),
            'max_depth': max((getattr(m, 'depth', 0) for m in messages), default=0),
            'participants': len(set(m.sender_id for m in messages))
        }

    def user_can_reply(self, root_message):
        """Check if user can reply to this conversation."""
        user = self.request.user
        return user == root_message.sender or user == root_message.receiver


@login_required
@require_POST
def send_threaded_reply(request, parent_id):
    """
    Send a reply to a specific message using optimized queries.
    
    This view demonstrates the sender=request.user pattern.
    """
    parent_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'), 
        id=parent_id
    )
    
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Content is required'}, status=400)
    
    # Determine receiver (opposite participant in conversation)
    if parent_message.sender == request.user:
        receiver = parent_message.receiver
    else:
        receiver = parent_message.sender
    
    # Create reply with sender=request.user
    reply = Message.objects.create(
        sender=request.user,  # This is the required pattern
        receiver=receiver,
        content=content,
        parent_message=parent_message,
        thread_level=parent_message.thread_level + 1
    )
    
    return JsonResponse({
        'success': True,
        'message_id': reply.id,
        'sender': reply.sender.username,
        'content': reply.content,
        'timestamp': reply.timestamp.isoformat()
    })


class NotificationListView(LoginRequiredMixin, ListView):
    """
    View to list notifications for the current user with optimized queries.
    
    Uses select_related and prefetch_related for efficient loading.
    """
    model = Notification
    template_name = 'messaging/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        """
        Return notifications for the current user with optimized prefetching.
        
        Uses select_related for foreign keys and prefetch_related to 
        optimize loading of related message data.
        """
        return Notification.objects.filter(
            user=self.request.user
        ).select_related(
            'user', 'message', 'message__sender', 'message__receiver'
        ).prefetch_related(
            # Prefetch message history for notifications about edited messages
            Prefetch(
                'message__history',
                queryset=MessageHistory.objects.select_related('edited_by').order_by('-version')[:3]
            ),
            # Prefetch message replies for thread context
            Prefetch(
                'message__replies',
                queryset=Message.objects.select_related('sender').order_by('timestamp')[:5]
            )
        ).order_by('-created_at')


class MessageHistoryView(LoginRequiredMixin, DetailView):
    """View to display the edit history of a message."""
    model = Message
    template_name = 'messaging/message_history.html'
    context_object_name = 'message'

    def get_context_data(self, **kwargs):
        """Add message history to the context."""
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        
        # Only allow viewing history for messages the user is involved in
        if (message.sender != self.request.user and 
            message.receiver != self.request.user):
            # Redirect or show error if user is not involved in the message
            context['access_denied'] = True
            return context
        
        # Get the history entries
        context['history_entries'] = MessageHistory.objects.filter(
            message=message
        ).order_by('version')
        
        return context


@login_required
def message_history_api(request, message_id):
    """API endpoint to get message history as JSON."""
    import json
    from django.http import JsonResponse
    
    message = get_object_or_404(Message, id=message_id)
    
    # Check permissions
    if message.sender != request.user and message.receiver != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get history entries
    history_entries = MessageHistory.objects.filter(
        message=message
    ).order_by('version')
    
    history_data = []
    for entry in history_entries:
        history_data.append({
            'version': entry.version,
            'old_content': entry.old_content,
            'edited_by': entry.edited_by.username,
            'edited_at': entry.edited_at.isoformat(),
        })
    
    return JsonResponse({
        'message_id': message.id,
        'current_content': message.content,
        'is_edited': message.edited,
        'edited_at': message.edited_at.isoformat() if message.edited_at else None,
        'history': history_data
    })


@login_required
def delete_user_confirmation(request):
    """View to show user deletion confirmation page."""
    if request.method == 'GET':
        # Show confirmation page with statistics
        user = request.user
        
        # Get user's data statistics
        sent_messages_count = Message.objects.filter(sender=user).count()
        received_messages_count = Message.objects.filter(receiver=user).count()
        notifications_count = Notification.objects.filter(user=user).count()
        message_edits_count = MessageHistory.objects.filter(edited_by=user).count()
        
        context = {
            'user': user,
            'sent_messages_count': sent_messages_count,
            'received_messages_count': received_messages_count,
            'notifications_count': notifications_count,
            'message_edits_count': message_edits_count,
            'total_data_points': (
                sent_messages_count + 
                received_messages_count + 
                notifications_count + 
                message_edits_count
            )
        }
        
        return render(request, 'messaging/delete_user_confirmation.html', context)


@login_required
@require_POST
@csrf_protect
def delete_user_account(request):
    """
    View to handle user account deletion.
    
    This view will delete the user account, and the post_delete signal
    will automatically clean up all related data.
    """
    user = request.user
    username = user.username
    
    try:
        # Log the user out first
        logout(request)
        
        # Delete the user account
        # The post_delete signal will handle cleanup of related data
        user.delete()
        
        # Add success message
        messages.success(
            request, 
            f'Account "{username}" has been successfully deleted along with all associated data.'
        )
        
        # Redirect to home page or registration page
        return redirect('/')
        
    except Exception as e:
        # Re-login the user if deletion failed
        messages.error(
            request,
            f'Failed to delete account: {str(e)}. Please try again or contact support.'
        )
        return redirect('messaging:delete_user_confirmation')


@login_required
def user_data_summary(request):
    """API endpoint to get user's data summary for deletion confirmation."""
    user = request.user
    
    # Get comprehensive data summary
    sent_messages = Message.objects.filter(sender=user)
    received_messages = Message.objects.filter(receiver=user)
    user_notifications = Notification.objects.filter(user=user)
    user_edits = MessageHistory.objects.filter(edited_by=user)
    
    # Get recent items as examples
    recent_sent = sent_messages.order_by('-timestamp')[:5]
    recent_received = received_messages.order_by('-timestamp')[:5]
    recent_notifications = user_notifications.order_by('-created_at')[:5]
    
    data = {
        'username': user.username,
        'email': user.email,
        'join_date': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'statistics': {
            'sent_messages': sent_messages.count(),
            'received_messages': received_messages.count(),
            'notifications': user_notifications.count(),
            'message_edits': user_edits.count(),
        },
        'recent_activity': {
            'sent_messages': [
                {
                    'id': msg.id,
                    'to': msg.receiver.username,
                    'content_preview': msg.content[:50] + '...' if len(msg.content) > 50 else msg.content,
                    'timestamp': msg.timestamp.isoformat()
                } for msg in recent_sent
            ],
            'received_messages': [
                {
                    'id': msg.id,
                    'from': msg.sender.username,
                    'content_preview': msg.content[:50] + '...' if len(msg.content) > 50 else msg.content,
                    'timestamp': msg.timestamp.isoformat()
                } for msg in recent_received
            ],
            'notifications': [
                {
                    'id': notif.id,
                    'type': notif.notification_type,
                    'title': notif.title,
                    'created_at': notif.created_at.isoformat()
                } for notif in recent_notifications
            ]
        }
    }
    
    return JsonResponse(data)
