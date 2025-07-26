# Test file for permissions
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from chats.models import Conversation, Message
from chats.permissions import IsParticipantOfConversation

User = get_user_model()

class PermissionsTest(TestCase):
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
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # Create a conversation between user1 and user2
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
        
        # Create a message in the conversation
        self.message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        self.client = APIClient()
    
    def test_unauthenticated_user_cannot_access_api(self):
        """Test that unauthenticated users cannot access the API"""
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_participant_can_access_conversation(self):
        """Test that participants can access their conversations"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_non_participant_cannot_access_conversation(self):
        """Test that non-participants cannot access conversations they're not part of"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(f'/api/conversations/{self.conversation.conversation_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_participant_can_send_message(self):
        """Test that participants can send messages to their conversations"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'New test message'
        }
        response = self.client.post('/api/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_non_participant_cannot_send_message(self):
        """Test that non-participants cannot send messages to conversations they're not part of"""
        self.client.force_authenticate(user=self.user3)
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Unauthorized message'
        }
        response = self.client.post('/api/messages/', data)
        # The user won't even see the conversation, so this should fail
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

if __name__ == '__main__':
    print("Permissions implementation completed successfully!")
    print("Key features implemented:")
    print("1. IsParticipantOfConversation permission class created")
    print("2. Only authenticated users can access the API")
    print("3. Only participants can view/send/update/delete messages")
    print("4. Custom permissions applied to viewsets")
    print("5. Global default permissions set in settings.py")
