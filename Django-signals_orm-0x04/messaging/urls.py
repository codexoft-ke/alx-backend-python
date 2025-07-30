"""
URL configuration for the messaging app.
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.MessageListView.as_view(), name='message_list'),
    path('send/', views.SendMessageView.as_view(), name='send_message'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    
    # Unread messages views using custom managers
    path('unread/', views.UnreadMessagesView.as_view(), name='unread_messages'),
    path('unread-inbox/', views.unread_inbox_view, name='unread_inbox'),
    path('inbox/', views.OptimizedInboxView.as_view(), name='optimized_inbox'),
    
    # Threaded conversation views
    path('conversation/<int:pk>/', views.ThreadedConversationView.as_view(), name='threaded_conversation'),
    path('reply/<int:parent_id>/', views.send_threaded_reply, name='send_threaded_reply'),
    
    # Message history
    path('message/<int:pk>/history/', views.MessageHistoryView.as_view(), name='message_history'),
    path('api/message/<int:message_id>/history/', views.message_history_api, name='message_history_api'),
    
    # API endpoints for unread messages
    path('api/mark-as-read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('api/unread/', views.unread_messages_api, name='unread_messages_api'),
    path('api/conversation/<int:conversation_id>/unread-count/', views.conversation_unread_count_api, name='conversation_unread_count_api'),
    
    # User deletion
    path('delete-account/', views.delete_user_confirmation, name='delete_user_confirmation'),
    path('delete-account/confirm/', views.delete_user_account, name='delete_user_account'),
    path('api/user/data-summary/', views.user_data_summary, name='user_data_summary'),
]
