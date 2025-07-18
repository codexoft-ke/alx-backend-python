from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for future viewsets
router = DefaultRouter()

# URL patterns for the chats app
urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    # Add your URL patterns here
    # Example: path('messages/', views.MessageListView.as_view(), name='message-list'),
]

# Include router URLs
urlpatterns += router.urls
