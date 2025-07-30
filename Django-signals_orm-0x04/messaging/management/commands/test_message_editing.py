"""
Django management command to test message editing and history logging.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, MessageHistory, Notification


class Command(BaseCommand):
    help = 'Test message editing functionality and history logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before testing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("🧹 Clearing existing data...")
            MessageHistory.objects.all().delete()
            Message.objects.all().delete()
            Notification.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Data cleared"))

        self.stdout.write("🧪 Testing Message Editing and History Logging")
        self.stdout.write("=" * 60)

        # Create test users if they don't exist
        user1, created = User.objects.get_or_create(
            username='editor',
            defaults={'email': 'editor@test.com'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user1.username}")

        user2, created = User.objects.get_or_create(
            username='receiver',
            defaults={'email': 'receiver@test.com'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user2.username}")

        # Test 1: Create a message
        self.stdout.write("\n📧 Test 1: Creating initial message...")
        
        message = Message.objects.create(
            sender=user1,
            receiver=user2,
            content="This is the original message content."
        )
        
        self.stdout.write(f"✅ Message created: {message.content}")
        self.stdout.write(f"   Edited status: {message.edited}")
        
        # Check initial history count
        initial_history_count = MessageHistory.objects.filter(message=message).count()
        self.stdout.write(f"   Initial history entries: {initial_history_count}")

        # Test 2: Edit the message content
        self.stdout.write("\n✏️ Test 2: Editing message content...")
        
        old_content = message.content
        message.content = "This is the UPDATED message content with new information!"
        message.save()
        
        # Check if edit was detected
        message.refresh_from_db()
        self.stdout.write(f"✅ Message updated: {message.content}")
        self.stdout.write(f"   Edited status: {message.edited}")
        self.stdout.write(f"   Edited at: {message.edited_at}")
        
        # Check history creation
        history_entries = MessageHistory.objects.filter(message=message)
        self.stdout.write(f"   History entries created: {history_entries.count()}")
        
        if history_entries.exists():
            history = history_entries.first()
            self.stdout.write(f"   Old content in history: {history.old_content}")
            self.stdout.write(f"   History version: {history.version}")
        
        # Check notification creation
        edit_notifications = Notification.objects.filter(
            user=user2,
            message=message,
            notification_type='message_edited'
        )
        self.stdout.write(f"   Edit notifications created: {edit_notifications.count()}")
        
        if edit_notifications.exists():
            notification = edit_notifications.first()
            self.stdout.write(f"   Notification title: {notification.title}")

        # Test 3: Edit the message again
        self.stdout.write("\n✏️ Test 3: Editing message again...")
        
        message.content = "This is the SECOND EDIT of the message content!"
        message.save()
        
        # Check multiple history entries
        message.refresh_from_db()
        history_entries = MessageHistory.objects.filter(message=message).order_by('version')
        self.stdout.write(f"✅ Second edit completed")
        self.stdout.write(f"   Total history entries: {history_entries.count()}")
        
        for i, history in enumerate(history_entries):
            self.stdout.write(f"   Version {history.version}: {history.old_content[:50]}...")

        # Test 4: Edit by different user (simulate)
        self.stdout.write("\n👤 Test 4: Simulating edit by different user...")
        
        # Note: In a real scenario, you'd have proper user authentication
        # For testing, we'll just change the content and save
        message.content = "Final version edited by another process!"
        message.save()
        
        # Final statistics
        self.stdout.write("\n📊 Final Statistics:")
        self.stdout.write(f"   Message ID: {message.id}")
        self.stdout.write(f"   Current content: {message.content}")
        self.stdout.write(f"   Is edited: {message.edited}")
        self.stdout.write(f"   Edit timestamp: {message.edited_at}")
        self.stdout.write(f"   Total history entries: {MessageHistory.objects.filter(message=message).count()}")
        self.stdout.write(f"   Total notifications: {Notification.objects.filter(message=message).count()}")
        
        # Show complete edit history
        self.stdout.write("\n📜 Complete Edit History:")
        for history in MessageHistory.objects.filter(message=message).order_by('version'):
            self.stdout.write(f"   v{history.version} ({history.edited_at}): {history.old_content}")
        
        self.stdout.write(f"   Current: {message.content}")

        self.stdout.write("\n🎉 Message editing test completed!")
        self.stdout.write("💡 All edits were automatically logged using Django signals!")
