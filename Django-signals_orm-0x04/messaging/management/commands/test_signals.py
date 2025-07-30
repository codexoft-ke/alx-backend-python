"""
Django management command to demonstrate signal functionality.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, Notification


class Command(BaseCommand):
    help = 'Test Django signals by creating messages and observing automatic notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing messages and notifications before testing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("🧹 Clearing existing data...")
            Message.objects.all().delete()
            Notification.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Data cleared"))

        self.stdout.write("🧪 Testing Django Signals for Automatic Notifications")
        self.stdout.write("=" * 60)

        # Create test users if they don't exist
        user1, created = User.objects.get_or_create(
            username='testuser1',
            defaults={'email': 'user1@test.com'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user1.username}")

        user2, created = User.objects.get_or_create(
            username='testuser2',
            defaults={'email': 'user2@test.com'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user2.username}")

        # Test 1: Send a message and check notification creation
        self.stdout.write("\n📧 Test 1: Sending message and checking automatic notification...")
        
        initial_notifications = Notification.objects.count()
        
        message = Message.objects.create(
            sender=user1,
            receiver=user2,
            content="Hello! This is a test message from Django signals."
        )
        
        final_notifications = Notification.objects.count()
        new_notifications = final_notifications - initial_notifications
        
        if new_notifications > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ {new_notifications} notification(s) created automatically!"))
            
            # Show the notification details
            notification = Notification.objects.filter(user=user2, message=message).first()
            if notification:
                self.stdout.write(f"   📬 Title: {notification.title}")
                self.stdout.write(f"   📝 Description: {notification.description}")
        else:
            self.stdout.write(self.style.ERROR("❌ No notifications were created"))

        # Test 2: Mark message as read and check read notification
        self.stdout.write("\n👀 Test 2: Marking message as read and checking read receipt...")
        
        initial_sender_notifications = Notification.objects.filter(user=user1).count()
        
        message.is_read = True
        message.save()
        
        final_sender_notifications = Notification.objects.filter(user=user1).count()
        new_sender_notifications = final_sender_notifications - initial_sender_notifications
        
        if new_sender_notifications > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ {new_sender_notifications} read notification(s) created for sender!"))
            
            read_notification = Notification.objects.filter(
                user=user1, 
                message=message, 
                notification_type='message_read'
            ).first()
            if read_notification:
                self.stdout.write(f"   📬 Title: {read_notification.title}")
        else:
            self.stdout.write(self.style.ERROR("❌ No read notifications were created"))

        # Show final statistics
        self.stdout.write("\n📊 Final Statistics:")
        self.stdout.write(f"   Total Messages: {Message.objects.count()}")
        self.stdout.write(f"   Total Notifications: {Notification.objects.count()}")
        self.stdout.write(f"   {user1.username}'s Notifications: {Notification.objects.filter(user=user1).count()}")
        self.stdout.write(f"   {user2.username}'s Notifications: {Notification.objects.filter(user=user2).count()}")

        self.stdout.write("\n🎉 Signal testing completed!")
        self.stdout.write("💡 Signals automatically created notifications without any manual intervention!")
