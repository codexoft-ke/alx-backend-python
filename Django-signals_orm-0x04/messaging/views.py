"""
Views for the messaging app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Message, Notification


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
