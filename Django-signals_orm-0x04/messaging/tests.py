"""
Tests for the messaging app.

This module contains comprehensive tests for the Message and Notification models,
as well as the Django signals that automatically create notifications.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from unittest.mock import patch
from .models import Message, Notification, UserProfile
from .signals import (
    create_message_notification,
    message_read_notification,
    create_user_profile,
    user_status_notification
)


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@test.com',
            password='testpass123'
        )

    def test_message_creation(self):
        """Test that a message can be created successfully."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.timestamp)

    def test_message_str_representation(self):
        """Test the string representation of a message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        expected_str = f"Message from {self.sender.username} to {self.receiver.username} at {message.timestamp}"
        self.assertEqual(str(message), expected_str)

    def test_mark_as_read(self):
        """Test marking a message as read."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        self.assertFalse(message.is_read)
        message.mark_as_read()
        self.assertTrue(message.is_read)

    def test_message_ordering(self):
        """Test that messages are ordered by timestamp descending."""
        message1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message"
        )
        
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Second message"
        )
        
        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)  # Most recent first
        self.assertEqual(messages[1], message1)


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        """Test that a notification can be created successfully."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.user,
            content="Test message"
        )
        
        notification = Notification.objects.create(
            user=self.user,
            message=message,
            notification_type='new_message',
            title='New message received',
            description='You have a new message'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'new_message')
        self.assertEqual(notification.title, 'New message received')
        self.assertFalse(notification.is_read)

    def test_notification_str_representation(self):
        """Test the string representation of a notification."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='new_message',
            title='Test notification'
        )
        
        expected_str = f"Notification for {self.user.username}: Test notification"
        self.assertEqual(str(notification), expected_str)

    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='new_message',
            title='Test notification'
        )
        
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)


class UserProfileModelTest(TestCase):
    """Test cases for the UserProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_user_profile_creation(self):
        """Test that a user profile is created automatically."""
        # UserProfile should be created automatically via signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertFalse(self.user.profile.is_online)

    def test_set_online(self):
        """Test setting user as online."""
        profile = self.user.profile
        profile.set_online()
        
        self.assertTrue(profile.is_online)
        self.assertIsNotNone(profile.last_seen)

    def test_set_offline(self):
        """Test setting user as offline."""
        profile = self.user.profile
        profile.set_online()
        profile.set_offline()
        
        self.assertFalse(profile.is_online)
        self.assertIsNotNone(profile.last_seen)


class MessageSignalTest(TestCase):
    """Test cases for message-related signals."""

    def setUp(self):
        """Set up test data."""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@test.com',
            password='testpass123'
        )

    def test_notification_created_on_new_message(self):
        """Test that a notification is created when a new message is sent."""
        # Count notifications before
        initial_count = Notification.objects.count()
        
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this triggers a notification!"
        )
        
        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        
        # Check the notification details
        notification = Notification.objects.filter(
            user=self.receiver,
            message=message,
            notification_type='new_message'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertIn(self.sender.username, notification.title)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        """Test that no new notification is created when updating an existing message."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        initial_count = Notification.objects.count()
        
        # Update the message content
        message.content = "Updated content"
        message.save()
        
        # Should not create a new notification
        self.assertEqual(Notification.objects.count(), initial_count)

    def test_read_notification_created(self):
        """Test that a read notification is created when message is marked as read."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        initial_count = Notification.objects.count()
        
        # Mark message as read
        message.is_read = True
        message.save()
        
        # Should create a read notification for the sender
        read_notifications = Notification.objects.filter(
            user=self.sender,
            message=message,
            notification_type='message_read'
        )
        
        self.assertEqual(read_notifications.count(), 1)
        notification = read_notifications.first()
        self.assertIn(self.receiver.username, notification.title)
        self.assertIn("read", notification.title.lower())

    def test_no_duplicate_read_notifications(self):
        """Test that duplicate read notifications are not created."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        # Mark as read multiple times
        message.is_read = True
        message.save()
        
        message.save()  # Save again
        message.save()  # Save again
        
        # Should only have one read notification
        read_notifications = Notification.objects.filter(
            user=self.sender,
            message=message,
            notification_type='message_read'
        )
        
        self.assertEqual(read_notifications.count(), 1)


class UserSignalTest(TestCase):
    """Test cases for user-related signals."""

    def test_user_profile_created_on_user_creation(self):
        """Test that a UserProfile is created when a new User is created."""
        user = User.objects.create_user(
            username='newuser',
            email='new@test.com',
            password='testpass123'
        )
        
        # Check that profile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
        self.assertFalse(user.profile.is_online)

    @patch('builtins.print')  # Mock print to avoid console output during tests
    def test_signal_handlers_are_called(self, mock_print):
        """Test that signal handlers are actually being called."""
        # Create a new message, which should trigger the signal
        sender = User.objects.create_user(username='sender', password='pass')
        receiver = User.objects.create_user(username='receiver', password='pass')
        
        Message.objects.create(
            sender=sender,
            receiver=receiver,
            content="Test signal message"
        )
        
        # Check that the print statement in the signal handler was called
        mock_print.assert_called()


class IntegrationTest(TestCase):
    """Integration tests for the complete messaging system."""

    def setUp(self):
        """Set up test data."""
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

    def test_complete_messaging_flow(self):
        """Test the complete flow: send message -> notification -> read -> read notification."""
        # Step 1: Send a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello user2!"
        )
        
        # Check that notification was created for receiver
        receiver_notifications = Notification.objects.filter(
            user=self.user2,
            message=message,
            notification_type='new_message'
        )
        self.assertEqual(receiver_notifications.count(), 1)
        
        # Step 2: Mark message as read
        message.is_read = True
        message.save()
        
        # Check that read notification was created for sender
        sender_notifications = Notification.objects.filter(
            user=self.user1,
            message=message,
            notification_type='message_read'
        )
        self.assertEqual(sender_notifications.count(), 1)
        
        # Step 3: Verify total notifications
        total_notifications = Notification.objects.filter(message=message)
        self.assertEqual(total_notifications.count(), 2)

    def test_multiple_messages_between_users(self):
        """Test multiple messages and their notifications."""
        # Send multiple messages
        messages = []
        for i in range(3):
            message = Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                content=f"Message {i+1}"
            )
            messages.append(message)
        
        # Check that each message generated a notification
        for message in messages:
            notification = Notification.objects.filter(
                user=self.user2,
                message=message,
                notification_type='new_message'
            ).first()
            self.assertIsNotNone(notification)
        
        # Total notifications should be 3
        notifications = Notification.objects.filter(
            user=self.user2,
            notification_type='new_message'
        )
        self.assertEqual(notifications.count(), 3)

    def test_cross_messaging(self):
        """Test messaging in both directions."""
        # User1 sends to User2
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello from user1"
        )
        
        # User2 sends to User1
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Hello from user2"
        )
        
        # Check notifications for both users
        user1_notifications = Notification.objects.filter(user=self.user1)
        user2_notifications = Notification.objects.filter(user=self.user2)
        
        self.assertEqual(user1_notifications.count(), 1)  # From message2
        self.assertEqual(user2_notifications.count(), 1)  # From message1
