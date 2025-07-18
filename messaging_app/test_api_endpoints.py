#!/usr/bin/env python
"""
Test script to validate API endpoints functionality
"""
import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append('/home/codexoft/Projects/Programming/Personal/School Assignments/ALX/alx-backend-python/messaging_app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.models import User, Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

def test_api_endpoints():
    """Test all API endpoints"""
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Test 1: Health check endpoint
    print("\n1. Testing Health Check...")
    response = client.get('/api/health/')
    if response.status_code == 200:
        print("   ✅ Health check passed")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
    
    # Test 2: Create test users
    print("\n2. Creating test users...")
    try:
        # Clean up existing test users
        User.objects.filter(username__startswith='testuser').delete()
        
        user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1'
        )
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2'
        )
        print("   ✅ Test users created successfully")
        
        # Login user1
        client.login(username='testuser1', password='testpass123')
        print("   ✅ User1 logged in")
        
    except Exception as e:
        print(f"   ❌ Error creating test users: {e}")
        return
    
    # Test 3: Test conversation endpoints
    print("\n3. Testing Conversation Endpoints...")
    try:
        # Create conversation
        conversation_data = {
            'participant_ids': [str(user1.user_id), str(user2.user_id)]
        }
        response = client.post(
            '/api/conversations/',
            data=json.dumps(conversation_data),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            print("   ✅ Conversation created successfully")
            conversation_id = response.json()['conversation_id']
            
            # List conversations
            response = client.get('/api/conversations/')
            if response.status_code == 200:
                print("   ✅ Conversations listed successfully")
                print(f"   📊 Found {len(response.json())} conversations")
            else:
                print(f"   ❌ Failed to list conversations: {response.status_code}")
                
        else:
            print(f"   ❌ Failed to create conversation: {response.status_code}")
            print(f"   Error: {response.json()}")
            return
            
    except Exception as e:
        print(f"   ❌ Error testing conversation endpoints: {e}")
        return
    
    # Test 4: Test message endpoints
    print("\n4. Testing Message Endpoints...")
    try:
        # Send message
        message_data = {
            'conversation': conversation_id,
            'message_body': 'Hello, this is a test message!'
        }
        response = client.post(
            '/api/messages/',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            print("   ✅ Message sent successfully")
            message_id = response.json()['message_id']
            
            # List messages
            response = client.get('/api/messages/')
            if response.status_code == 200:
                print("   ✅ Messages listed successfully")
                print(f"   📊 Found {len(response.json())} messages")
            else:
                print(f"   ❌ Failed to list messages: {response.status_code}")
                
        else:
            print(f"   ❌ Failed to send message: {response.status_code}")
            print(f"   Error: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Error testing message endpoints: {e}")
    
    # Test 5: Test user endpoints
    print("\n5. Testing User Endpoints...")
    try:
        # Get current user
        response = client.get('/api/users/me/')
        if response.status_code == 200:
            print("   ✅ Current user retrieved successfully")
        else:
            print(f"   ❌ Failed to get current user: {response.status_code}")
        
        # Search users
        response = client.get('/api/users/search/?q=test')
        if response.status_code == 200:
            print("   ✅ User search successful")
            print(f"   📊 Found {len(response.json())} users")
        else:
            print(f"   ❌ Failed to search users: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing user endpoints: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API endpoint tests completed!")

if __name__ == "__main__":
    test_api_endpoints()
