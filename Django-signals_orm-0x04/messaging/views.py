"""
Views for the messaging app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
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
