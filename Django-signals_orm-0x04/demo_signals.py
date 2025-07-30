#!/usr/bin/env python
"""
Django Signals Demonstration Script

This script demonstrates the automatic notification system using Django signals.
It creates users, sends messages, and shows how notifications are automatically created.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, Notification, UserProfile


def create_demo_users():
    """Create demo users for testing."""
    print("🔧 Creating demo users...")
    
    # Create users (UserProfile will be created automatically via signals)
    alice, created = User.objects.get_or_create(
        username='alice',
        defaults={
            'email': 'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith'
        }
    )
    if created:
        alice.set_password('demo123')
        alice.save()
    
    bob, created = User.objects.get_or_create(
        username='bob',
        defaults={
            'email': 'bob@example.com',
            'first_name': 'Bob',
            'last_name': 'Johnson'
        }
    )
    if created:
        bob.set_password('demo123')
        bob.save()
    
    charlie, created = User.objects.get_or_create(
        username='charlie',
        defaults={
            'email': 'charlie@example.com',
            'first_name': 'Charlie',
            'last_name': 'Brown'
        }
    )
    if created:
        charlie.set_password('demo123')
        charlie.save()
    
    print(f"✅ Users created: {alice.username}, {bob.username}, {charlie.username}")
    return alice, bob, charlie


def demonstrate_messaging_signals(alice, bob, charlie):
    """Demonstrate how signals create notifications automatically."""
    print("\n📧 Demonstrating message signals...")
    
    # Clear existing messages and notifications for clean demo
    Message.objects.all().delete()
    Notification.objects.all().delete()
    
    print(f"📊 Initial state:")
    print(f"   Messages: {Message.objects.count()}")
    print(f"   Notifications: {Notification.objects.count()}")
    
    # Alice sends a message to Bob
    print(f"\n💬 Alice sends message to Bob...")
    message1 = Message.objects.create(
        sender=alice,
        receiver=bob,
        content="Hi Bob! How are you doing today?"
    )
    
    # Check notifications (should be created automatically)
    bob_notifications = Notification.objects.filter(user=bob)
    print(f"✅ Notifications created for Bob: {bob_notifications.count()}")
    if bob_notifications.exists():
        notification = bob_notifications.first()
        print(f"   📬 Notification: {notification.title}")
        print(f"   📝 Description: {notification.description}")
    
    # Bob sends a reply to Alice
    print(f"\n💬 Bob replies to Alice...")
    message2 = Message.objects.create(
        sender=bob,
        receiver=alice,
        content="Hi Alice! I'm doing great, thanks for asking. How about you?"
    )
    
    # Check Alice's notifications
    alice_notifications = Notification.objects.filter(user=alice)
    print(f"✅ Notifications created for Alice: {alice_notifications.count()}")
    
    # Alice reads Bob's message (this should create a read notification for Bob)
    print(f"\n👀 Alice reads Bob's message...")
    message2.is_read = True
    message2.save()
    
    # Check Bob's notifications for read receipt
    bob_read_notifications = Notification.objects.filter(
        user=bob,
        notification_type='message_read'
    )
    print(f"✅ Read notifications created for Bob: {bob_read_notifications.count()}")
    
    # Charlie joins the conversation
    print(f"\n💬 Charlie sends message to Alice...")
    message3 = Message.objects.create(
        sender=charlie,
        receiver=alice,
        content="Hey Alice! Can I join your conversation?"
    )
    
    # Show final statistics
    print(f"\n📊 Final statistics:")
    print(f"   Total messages: {Message.objects.count()}")
    print(f"   Total notifications: {Notification.objects.count()}")
    print(f"   Alice's notifications: {Notification.objects.filter(user=alice).count()}")
    print(f"   Bob's notifications: {Notification.objects.filter(user=bob).count()}")
    print(f"   Charlie's notifications: {Notification.objects.filter(user=charlie).count()}")


def demonstrate_user_profiles(alice, bob, charlie):
    """Demonstrate user profile functionality."""
    print("\n👤 Demonstrating user profiles...")
    
    # Show that profiles were created automatically
    print(f"✅ User profiles:")
    for user in [alice, bob, charlie]:
        profile = user.profile
        print(f"   {user.username}: Online={profile.is_online}, Last seen={profile.last_seen}")
    
    # Set Alice online
    print(f"\n🟢 Setting Alice online...")
    alice.profile.set_online()
    print(f"   Alice online status: {alice.profile.is_online}")
    
    # Set Bob offline
    print(f"\n⚫ Setting Bob offline...")
    bob.profile.set_offline()
    print(f"   Bob online status: {bob.profile.is_online}")


def show_detailed_notifications():
    """Show detailed view of all notifications."""
    print("\n📋 Detailed notification report:")
    print("=" * 60)
    
    notifications = Notification.objects.all().order_by('-created_at')
    for i, notification in enumerate(notifications, 1):
        print(f"{i}. {notification.title}")
        print(f"   👤 User: {notification.user.username}")
        print(f"   📧 Type: {notification.notification_type}")
        print(f"   📝 Description: {notification.description}")
        print(f"   👀 Read: {'Yes' if notification.is_read else 'No'}")
        print(f"   🕒 Created: {notification.created_at}")
        if notification.message:
            print(f"   📨 Related message: #{notification.message.id}")
        print("-" * 40)


def main():
    """Main demonstration function."""
    print("🚀 Django Signals Notification System Demo")
    print("=" * 50)
    
    # Create demo users
    alice, bob, charlie = create_demo_users()
    
    # Demonstrate messaging with automatic notifications
    demonstrate_messaging_signals(alice, bob, charlie)
    
    # Demonstrate user profiles
    demonstrate_user_profiles(alice, bob, charlie)
    
    # Show detailed notification report
    show_detailed_notifications()
    
    print("\n🎉 Demo completed successfully!")
    print("\n💡 Key takeaways:")
    print("   • Notifications are created automatically when messages are sent")
    print("   • Read receipts are generated when messages are marked as read")
    print("   • User profiles are created automatically for new users")
    print("   • No manual intervention required - everything happens via Django signals!")
    
    print(f"\n🔗 Access Django Admin at: http://127.0.0.1:8000/admin/")
    print("   Username/Password: Create a superuser with 'python manage.py createsuperuser'")


if __name__ == '__main__':
    main()
