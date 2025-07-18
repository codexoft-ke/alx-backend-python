from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for viewsets - Using Django REST Framework DefaultRouter
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'users', views.UserViewSet, basename='user')

# URL patterns for the chats app
urlpatterns = [
    # Legacy endpoints
    path('health/', views.health_check, name='health-check'),
    path('test-serializers/', views.test_serializers, name='test-serializers'),
    
    # API endpoints
    path('conversations/create/', views.create_conversation, name='create-conversation'),
    path('conversations/<uuid:conversation_id>/send-message/', views.send_message, name='send-message'),
    
    # Include router URLs
    path('', include(router.urls)),
]
