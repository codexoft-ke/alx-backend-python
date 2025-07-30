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
    path('message/<int:pk>/history/', views.MessageHistoryView.as_view(), name='message_history'),
    path('api/message/<int:message_id>/history/', views.message_history_api, name='message_history_api'),
    path('delete-account/', views.delete_user_confirmation, name='delete_user_confirmation'),
    path('delete-account/confirm/', views.delete_user_account, name='delete_user_account'),
    path('api/user/data-summary/', views.user_data_summary, name='user_data_summary'),
]
