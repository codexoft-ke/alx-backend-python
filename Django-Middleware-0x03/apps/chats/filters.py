# Custom filters for chats app
import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages to retrieve conversations with specific users 
    or messages within a time range
    """
    # Filter by specific user (sender)
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        help_text="Filter messages by sender"
    )
    
    # Filter by sender username
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text="Filter messages by sender username (case-insensitive)"
    )
    
    # Filter by conversation
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        help_text="Filter messages by conversation"
    )
    
    # Filter by message content
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text="Filter messages by content (case-insensitive)"
    )
    
    # Time range filters
    sent_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text="Filter messages sent after this date/time (ISO format)"
    )
    
    sent_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text="Filter messages sent before this date/time (ISO format)"
    )
    
    # Date range filter
    sent_at_range = django_filters.DateFromToRangeFilter(
        field_name='sent_at',
        help_text="Filter messages within a date range"
    )
    
    # Filter by specific date
    sent_date = django_filters.DateFilter(
        field_name='sent_at__date',
        help_text="Filter messages sent on a specific date"
    )
    
    class Meta:
        model = Message
        fields = [
            'sender',
            'sender_username', 
            'conversation',
            'message_body',
            'sent_after',
            'sent_before',
            'sent_at_range',
            'sent_date'
        ]


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for conversations to retrieve conversations with specific users
    """
    # Filter by participant username
    participant = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text="Filter conversations by participant username"
    )
    
    # Filter by participant email
    participant_email = django_filters.CharFilter(
        field_name='participants__email',
        lookup_expr='icontains',
        help_text="Filter conversations by participant email"
    )
    
    # Filter by multiple participants
    participants = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        help_text="Filter conversations by specific participants"
    )
    
    # Time range filters for conversations
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter conversations created after this date/time"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter conversations created before this date/time"
    )
    
    updated_after = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        help_text="Filter conversations updated after this date/time"
    )
    
    updated_before = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        help_text="Filter conversations updated before this date/time"
    )
    
    class Meta:
        model = Conversation
        fields = [
            'participant',
            'participant_email',
            'participants',
            'created_after',
            'created_before',
            'updated_after',
            'updated_before'
        ]
