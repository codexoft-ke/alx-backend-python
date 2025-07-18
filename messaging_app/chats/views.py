from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, 
    ConversationSerializer, 
    ConversationDetailSerializer,
    ConversationSimpleSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageSimpleSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    Provides CRUD operations for conversations
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """
        Filter conversations to only show those where the user is a participant
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages').distinct()
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        elif self.action == 'list':
            return ConversationSimpleSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """
        Create a new conversation and add the current user as a participant
        """
        conversation = serializer.save()
        # Add the current user as a participant if not already included
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': f'User {user.username} added to conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response(
                {'message': f'User {user.username} removed from conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages in a conversation
        """
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSimpleSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    Provides CRUD operations for messages
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['conversation', 'sender']
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """
        Filter messages to only show those from conversations where the user is a participant
        """
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').distinct()
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action == 'list':
            return MessageSimpleSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """
        Create a new message with the current user as sender
        """
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        """
        Get all messages sent by the current user
        """
        messages = Message.objects.filter(
            sender=request.user
        ).select_related('conversation').order_by('-sent_at')
        
        serializer = MessageSimpleSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a message as read (placeholder for future implementation)
        """
        message = self.get_object()
        return Response(
            {'message': f'Message {message.message_id} marked as read'},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user operations (read-only for now)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    ordering = ['username']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for users by username or email
        """
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response(
                {'error': 'Query must be at least 2 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(user_id=request.user.user_id)[:10]
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


# Legacy endpoints for backwards compatibility
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify the API is working
    """
    return Response({
        'status': 'success',
        'message': 'Messaging app API is running!',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_serializers(request):
    """
    Test endpoint to verify serializers are working with sample data
    """
    try:
        # Get sample data if it exists
        users = User.objects.all()[:2]
        conversations = Conversation.objects.all()[:1]
        messages = Message.objects.all()[:2]
        
        # Serialize the data
        users_data = UserSerializer(users, many=True).data
        conversations_data = ConversationSerializer(conversations, many=True).data
        messages_data = MessageSerializer(messages, many=True).data
        
        return Response({
            'status': 'success',
            'message': 'Serializers are working correctly!',
            'data': {
                'users_count': len(users_data),
                'conversations_count': len(conversations_data),
                'messages_count': len(messages_data),
                'sample_user': users_data[0] if users_data else None,
                'sample_conversation': conversations_data[0] if conversations_data else None,
                'sample_message': messages_data[0] if messages_data else None
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error testing serializers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """
    Create a new conversation with participants
    """
    serializer = ConversationSerializer(data=request.data)
    if serializer.is_valid():
        conversation = serializer.save()
        # Add current user as participant if not already included
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            conversation.participants.add(request.user)
        
        response_serializer = ConversationDetailSerializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id):
    """
    Send a message to an existing conversation
    """
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        
        # Check if user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create message
        message_data = request.data.copy()
        message_data['conversation'] = conversation.conversation_id
        
        serializer = MessageCreateSerializer(
            data=message_data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            response_serializer = MessageSerializer(message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
