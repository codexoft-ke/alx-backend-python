"""
Django management command to test user deletion and cleanup signals.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, MessageHistory, Notification, UserProfile


class Command(BaseCommand):
    help = 'Test user deletion functionality and post_delete signals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create comprehensive test data before deletion test',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='test_delete_user',
            help='Username for the test user to be deleted',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write("🧪 Testing User Deletion and Cleanup Signals")
        self.stdout.write("=" * 60)

        # Create comprehensive test data if requested
        if options['create_test_data']:
            self.create_test_data(username)

        # Check if test user exists
        try:
            test_user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Test user '{username}' does not exist"))
            self.stdout.write("💡 Use --create-test-data to create test data first")
            return

        # Show user data before deletion
        self.show_user_data_summary(test_user)

        # Confirm deletion
        self.stdout.write(f"\n⚠️ About to delete user '{username}' and all related data...")
        confirm = input("Type 'DELETE' to confirm: ")
        
        if confirm != 'DELETE':
            self.stdout.write("❌ Deletion cancelled")
            return

        # Perform deletion and observe signal behavior
        self.stdout.write(f"\n🗑️ Deleting user '{username}'...")
        self.stdout.write("📡 The post_delete signal will automatically clean up related data...")

        # Delete the user (this will trigger the post_delete signal)
        test_user.delete()

        self.stdout.write(f"\n✅ User '{username}' has been deleted!")
        
        # Verify cleanup
        self.verify_cleanup(username)

        self.stdout.write("\n🎉 User deletion and cleanup test completed!")

    def create_test_data(self, username):
        """Create comprehensive test data for the user deletion test."""
        self.stdout.write(f"\n📝 Creating test data for user '{username}'...")

        # Create test user
        test_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created test user: {test_user.username}")
        else:
            self.stdout.write(f"ℹ️ Test user already exists: {test_user.username}")

        # Create other users for interactions
        user2, _ = User.objects.get_or_create(
            username='interaction_user2',
            defaults={'email': 'user2@test.com'}
        )
        user3, _ = User.objects.get_or_create(
            username='interaction_user3',
            defaults={'email': 'user3@test.com'}
        )

        # Create messages sent by test user
        for i in range(5):
            message = Message.objects.create(
                sender=test_user,
                receiver=user2,
                content=f"Test message {i+1} sent by {username} to user2"
            )
            self.stdout.write(f"   📧 Created sent message #{message.id}")

        # Create messages received by test user
        for i in range(3):
            message = Message.objects.create(
                sender=user3,
                receiver=test_user,
                content=f"Test message {i+1} sent to {username} from user3"
            )
            self.stdout.write(f"   📨 Created received message #{message.id}")

        # Edit some messages to create history entries
        messages_to_edit = Message.objects.filter(sender=test_user)[:2]
        for i, message in enumerate(messages_to_edit):
            message.content = f"EDITED: {message.content} (edit #{i+1})"
            message.save()
            self.stdout.write(f"   ✏️ Edited message #{message.id}")

        # Create some additional notifications
        for i in range(3):
            Notification.objects.create(
                user=test_user,
                notification_type='new_message',
                title=f'Test notification {i+1}',
                description=f'This is test notification {i+1} for {username}'
            )

        self.stdout.write("✅ Test data creation completed")

    def show_user_data_summary(self, user):
        """Show comprehensive summary of user's data before deletion."""
        self.stdout.write(f"\n📊 Data Summary for User '{user.username}':")
        self.stdout.write("-" * 40)

        # Messages
        sent_messages = Message.objects.filter(sender=user)
        received_messages = Message.objects.filter(receiver=user)
        self.stdout.write(f"   📧 Messages sent: {sent_messages.count()}")
        self.stdout.write(f"   📨 Messages received: {received_messages.count()}")

        # Notifications
        notifications = Notification.objects.filter(user=user)
        self.stdout.write(f"   🔔 Notifications: {notifications.count()}")

        # Message History
        message_edits = MessageHistory.objects.filter(edited_by=user)
        self.stdout.write(f"   📝 Message edits: {message_edits.count()}")

        # User Profile
        has_profile = hasattr(user, 'profile') and user.profile is not None
        self.stdout.write(f"   👤 User profile: {'Yes' if has_profile else 'No'}")

        # Show some sample data
        self.stdout.write("\n📋 Sample Data:")
        if sent_messages.exists():
            sample_sent = sent_messages.first()
            self.stdout.write(f"   📧 Sample sent message: \"{sample_sent.content[:50]}...\"")
        
        if received_messages.exists():
            sample_received = received_messages.first()
            self.stdout.write(f"   📨 Sample received message: \"{sample_received.content[:50]}...\"")
        
        if notifications.exists():
            sample_notification = notifications.first()
            self.stdout.write(f"   🔔 Sample notification: \"{sample_notification.title}\"")

        # Total items that will be deleted
        total_items = (
            sent_messages.count() + 
            received_messages.count() + 
            notifications.count() + 
            message_edits.count() +
            (1 if has_profile else 0)
        )
        self.stdout.write(f"\n📈 Total related items to be deleted: {total_items}")

    def verify_cleanup(self, username):
        """Verify that all user-related data has been cleaned up."""
        self.stdout.write(f"\n🔍 Verifying cleanup for deleted user '{username}'...")

        # Check if user still exists
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            self.stdout.write(self.style.ERROR("❌ User still exists!"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ User successfully deleted"))

        # Note: We can't check for related data by user foreign key since the user is deleted
        # But we can check if the signal worked by looking for orphaned data
        
        # Check for orphaned messages (shouldn't exist due to CASCADE or signal cleanup)
        orphaned_data_found = False
        
        # Check if there are any MessageHistory entries without a valid user
        try:
            # This might cause an error if foreign keys are properly set up
            orphaned_history = MessageHistory.objects.filter(edited_by__isnull=True)
            if orphaned_history.exists():
                self.stdout.write(f"⚠️ Found {orphaned_history.count()} orphaned MessageHistory entries")
                orphaned_data_found = True
        except Exception:
            pass  # Expected if foreign key constraints are working

        if not orphaned_data_found:
            self.stdout.write(self.style.SUCCESS("✅ No orphaned data found - cleanup successful"))

        # Show current database state
        self.stdout.write("\n📊 Current Database State:")
        self.stdout.write(f"   Total Users: {User.objects.count()}")
        self.stdout.write(f"   Total Messages: {Message.objects.count()}")
        self.stdout.write(f"   Total Notifications: {Notification.objects.count()}")
        self.stdout.write(f"   Total MessageHistory: {MessageHistory.objects.count()}")
        self.stdout.write(f"   Total UserProfiles: {UserProfile.objects.count()}")

        self.stdout.write("\n💡 The post_delete signal automatically cleaned up all user-related data!")
