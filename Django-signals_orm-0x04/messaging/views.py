"""
Views for the messaging app.
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
from .models import Message, Notification, MessageHistory


class MessageListView(LoginRequiredMixin, ListView):
    """View to list messages for the current user."""
    model = Message
    template_name = 'messaging/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        """Return messages for the current user."""
        return Message.objects.filter(
            receiver=self.request.user
        ).select_related('sender')


class SendMessageView(LoginRequiredMixin, CreateView):
    """View to send a new message."""
    model = Message
    fields = ['receiver', 'content']
    template_name = 'messaging/send_message.html'
    success_url = reverse_lazy('messaging:message_list')

    def form_valid(self, form):
        """Set the sender to the current user."""
        form.instance.sender = self.request.user
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)


class NotificationListView(LoginRequiredMixin, ListView):
    """View to list notifications for the current user."""
    model = Notification
    template_name = 'messaging/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('message')


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
