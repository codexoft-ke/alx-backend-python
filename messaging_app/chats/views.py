from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer


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
