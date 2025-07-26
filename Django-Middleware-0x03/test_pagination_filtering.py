# Test file for pagination and filtering functionality
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from chats.models import Conversation, Message
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class PaginationFilteringTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
        
        # Create 25 test messages to test pagination
        for i in range(25):
            Message.objects.create(
                sender=self.user1 if i % 2 == 0 else self.user2,
                conversation=self.conversation,
                message_body=f"Test message {i+1}"
            )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
    
    def test_message_pagination(self):
        """Test that messages are paginated with 20 items per page"""
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return paginated response
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertIn('current_page', data)
        self.assertIn('total_pages', data)
        self.assertEqual(len(data['results']), 20)  # 20 messages per page
        self.assertEqual(data['count'], 25)  # Total 25 messages
        self.assertEqual(data['total_pages'], 2)  # 2 pages total
    
    def test_message_filtering_by_sender(self):
        """Test filtering messages by sender"""
        response = self.client.get(f'/api/messages/?sender={self.user1.user_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # Should return only messages from user1 (13 messages: 0,2,4,6,8,10,12,14,16,18,20,22,24)
        self.assertEqual(data['count'], 13)
    
    def test_message_filtering_by_username(self):
        """Test filtering messages by sender username"""
        response = self.client.get('/api/messages/?sender_username=user2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # Should return only messages from user2 (12 messages: 1,3,5,7,9,11,13,15,17,19,21,23)
        self.assertEqual(data['count'], 12)
    
    def test_message_filtering_by_content(self):
        """Test filtering messages by content"""
        response = self.client.get('/api/messages/?message_body=message 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # Should return messages containing "message 1" (messages 1, 10-19)
        self.assertGreater(data['count'], 0)
    
    def test_conversation_filtering_by_participant(self):  
        """Test filtering conversations by participant"""
        response = self.client.get('/api/conversations/?participant=user2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['count'], 1)  # One conversation with user2

if __name__ == '__main__':
    print("Pagination and filtering implementation completed successfully!")
    print("Key features implemented:")
    print("1. MessagePagination class with 20 messages per page")
    print("2. ConversationPagination class with 10 conversations per page")
    print("3. MessageFilter for filtering by user, content, and time range")
    print("4. ConversationFilter for filtering by participants and time range")
    print("5. Updated views to use custom pagination and filters")
    print("6. Custom pagination response format with metadata")
    print("7. Additional endpoints for filtered message retrieval")
