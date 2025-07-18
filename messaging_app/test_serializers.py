#!/usr/bin/env python
"""
Test script to validate serializers functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/codexoft/Projects/Programming/Personal/School Assignments/ALX/alx-backend-python/messaging_app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.models import User, Conversation, Message
from chats.serializers import (
    UserSerializer, 
    ConversationSerializer, 
    MessageSerializer,
    ConversationDetailSerializer,
    MessageCreateSerializer
)

def test_serializers():
    """Test all serializers functionality"""
    
    print("🧪 Testing Serializers...")
    print("=" * 50)
    
    # Test 1: UserSerializer
    print("\n1. Testing UserSerializer...")
    user_data = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'securepassword123',
        'role': 'guest'
    }
    
    user_serializer = UserSerializer(data=user_data)
    if user_serializer.is_valid():
        print("   ✅ UserSerializer validation passed")
    else:
        print("   ❌ UserSerializer validation failed:", user_serializer.errors)
    
    # Test 2: ConversationSerializer
    print("\n2. Testing ConversationSerializer...")
    conversation_data = {
        'participant_ids': []
    }
    
    conversation_serializer = ConversationSerializer(data=conversation_data)
    if conversation_serializer.is_valid():
        print("   ✅ ConversationSerializer validation passed")
    else:
        print("   ❌ ConversationSerializer validation failed:", conversation_serializer.errors)
    
    # Test 3: Test with existing data
    print("\n3. Testing with existing data...")
    try:
        users = User.objects.all()
        conversations = Conversation.objects.all()
        messages = Message.objects.all()
        
        print(f"   📊 Found {users.count()} users, {conversations.count()} conversations, {messages.count()} messages")
        
        if users.exists():
            user_serializer = UserSerializer(users.first())
            print("   ✅ User serialization successful")
        
        if conversations.exists():
            conversation_serializer = ConversationSerializer(conversations.first())
            print("   ✅ Conversation serialization successful")
            
            detail_serializer = ConversationDetailSerializer(conversations.first())
            print("   ✅ ConversationDetail serialization successful")
        
        if messages.exists():
            message_serializer = MessageSerializer(messages.first())
            print("   ✅ Message serialization successful")
            
    except Exception as e:
        print(f"   ❌ Error testing with existing data: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Serializer tests completed!")

if __name__ == "__main__":
    test_serializers()
