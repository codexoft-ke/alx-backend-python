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
]
