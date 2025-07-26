# Custom permissions for chats app
from rest_framework import permissions
from .models import Conversation, Message


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to the owner of the object.
        return obj.user == request.user


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants in a conversation to send, view, update and delete messages.
    Also ensures only authenticated users can access the API.
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users to access the API
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Allow only participants in a conversation to send, view, update and delete messages
        """
        # Handle different HTTP methods for messages and conversations
        if request.method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            # Handle different object types
            if isinstance(obj, Message):
                # For messages, check if user is participant of the conversation
                return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            
            elif isinstance(obj, Conversation):
                # For conversations, check if user is participant
                return obj.participants.filter(user_id=request.user.user_id).exists()
            
            # For other objects, check if they have a user or sender field
            if hasattr(obj, 'sender'):
                return obj.sender == request.user
            elif hasattr(obj, 'user'):
                return obj.user == request.user
        
        # Default deny access
        return False
