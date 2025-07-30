"""
Django management command to test custom ORM managers for unread messages.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, Notification
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Test custom ORM managers for unread messages with .only() optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before testing',
        )
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Create test data for demonstration',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("🧹 Clearing existing data...")
            Message.objects.all().delete()
            Notification.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Data cleared"))

        self.stdout.write("🧪 Testing Custom ORM Managers for Unread Messages")
        self.stdout.write("=" * 65)

        # Create test users
        user1, created = User.objects.get_or_create(
            username='alice',
            defaults={'email': 'alice@test.com', 'first_name': 'Alice', 'last_name': 'Smith'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user1.username}")

        user2, created = User.objects.get_or_create(
            username='bob',
            defaults={'email': 'bob@test.com', 'first_name': 'Bob', 'last_name': 'Johnson'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user2.username}")

        user3, created = User.objects.get_or_create(
            username='charlie',
            defaults={'email': 'charlie@test.com', 'first_name': 'Charlie', 'last_name': 'Brown'}
        )
        if created:
            self.stdout.write(f"✅ Created user: {user3.username}")

        # Create test data if requested
        if options['create_data']:
            self.create_test_data(user1, user2, user3)

        # Test 1: Basic UnreadMessagesManager functionality
        self.stdout.write("\n📧 Test 1: Testing UnreadMessagesManager.for_user()")
        
        # Get unread messages for user1 using custom manager
        unread_messages = Message.unread.for_user(user1)
        self.stdout.write(f"   Unread messages for {user1.username}: {unread_messages.count()}")
        
        # Display the optimized query (shows only() fields being used)
        self.stdout.write(f"   Query optimization: {unread_messages.query}")
        
        # Show first few unread messages
        for message in unread_messages[:3]:
            self.stdout.write(f"   📨 From {message.sender.username}: {message.content[:30]}...")

        # Test 2: Count functionality
        self.stdout.write("\n🔢 Test 2: Testing count functionality")
        
        unread_count = Message.unread.count_for_user(user1)
        total_count = Message.objects.filter(receiver=user1).count()
        read_count = Message.read.for_user(user1).count()
        
        self.stdout.write(f"   {user1.username}'s message statistics:")
        self.stdout.write(f"   📨 Total messages: {total_count}")
        self.stdout.write(f"   ✉️  Unread messages: {unread_count}")
        self.stdout.write(f"   ✅ Read messages: {read_count}")

        # Test 3: Optimized inbox view
        self.stdout.write("\n📥 Test 3: Testing optimized inbox with .only() fields")
        
        inbox_messages = Message.unread.inbox_for_user(user1, limit=5)
        self.stdout.write(f"   Optimized inbox query: {inbox_messages.query}")
        
        for message in inbox_messages:
            # Demonstrate that only specific fields are loaded
            self.stdout.write(f"   📨 {message.sender.username} -> {message.content[:20]}... ({message.timestamp})")

        # Test 4: Conversation threads with unread counts
        self.stdout.write("\n💬 Test 4: Testing conversation threads manager")
        
        conversations = Message.conversations.with_unread_count(user1)[:5]
        for conversation in conversations:
            self.stdout.write(f"   🗣️  Conversation #{conversation.id} - Unread: {conversation.unread_count}")

        # Test 5: Bulk operations performance test
        self.stdout.write("\n⚡ Test 5: Testing bulk mark-as-read performance")
        
        start_time = timezone.now()
        
        # Mark all unread messages as read for user1
        updated_count = Message.objects.filter(
            receiver=user1,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(f"   ✅ Marked {updated_count} messages as read in {duration:.3f} seconds")

        # Test 6: Custom manager method demonstration
        self.stdout.write("\n📊 Test 6: Testing custom manager methods")
        
        # Use the custom class method for inbox summary
        inbox_summary = Message.get_inbox_summary(user1)
        self.stdout.write(f"   📈 Inbox Summary for {user1.username}:")
        for key, value in inbox_summary.items():
            self.stdout.write(f"      {key}: {value}")

        # Test 7: .only() optimization demonstration
        self.stdout.write("\n🚀 Test 7: Demonstrating .only() optimization")
        
        # Show difference between full object loading and optimized loading
        self.stdout.write("   Full object query (loads all fields):")
        full_messages = Message.objects.filter(receiver=user2)[:3]
        for msg in full_messages:
            self.stdout.write(f"   📨 Full: {msg.id} - {msg.content[:20]}...")
        
        self.stdout.write("   Optimized query (loads only necessary fields):")
        optimized_messages = Message.objects.filter(receiver=user2).select_related('sender').only(
            'id', 'sender__username', 'content', 'timestamp', 'is_read'
        )[:3]
        for msg in optimized_messages:
            self.stdout.write(f"   ⚡ Optimized: {msg.id} - {msg.sender.username} - {msg.content[:20]}...")

        # Test 8: Advanced querying with prefetch_related
        self.stdout.write("\n🔧 Test 8: Advanced querying with threading support")
        
        # Get conversation threads with optimized prefetching
        threads = Message.conversations.for_user(user2).prefetch_related(
            'replies__sender',
            'replies__receiver'
        )[:3]
        
        for thread in threads:
            reply_count = thread.replies.count()
            self.stdout.write(f"   🧵 Thread #{thread.id}: {reply_count} replies")
            
            # Show first few replies (already prefetched, no additional queries)
            for reply in thread.replies.all()[:2]:
                self.stdout.write(f"      ↳ Reply by {reply.sender.username}: {reply.content[:25]}...")

        # Final statistics
        self.stdout.write("\n📊 Final Statistics:")
        for user in [user1, user2, user3]:
            stats = Message.get_inbox_summary(user)
            self.stdout.write(f"   👤 {user.username}:")
            self.stdout.write(f"      Total: {stats['total_messages']}, Unread: {stats['unread_count']}")

        self.stdout.write("\n🎉 Custom ORM Manager testing completed!")
        self.stdout.write("💡 Custom managers provide optimized queries with .only() fields for better performance!")

    def create_test_data(self, user1, user2, user3):
        """Create test messages for demonstration."""
        self.stdout.write("📝 Creating test data...")
        
        # Create various types of messages
        messages = [
            # Unread messages for user1
            ("Hello Alice, how are you?", user2, user1, False),
            ("Quick question about the project", user3, user1, False),
            ("Meeting reminder for tomorrow", user2, user1, False),
            ("Can you review this document?", user3, user1, False),
            
            # Mix of read/unread for user2
            ("Thanks for your help!", user1, user2, True),
            ("New update available", user3, user2, False),
            ("Lunch plans?", user1, user2, False),
            
            # Messages for user3
            ("Project completed successfully", user1, user3, True),
            ("Need your input on design", user2, user3, False),
            ("Conference call at 3 PM", user1, user3, False),
        ]
        
        created_count = 0
        for content, sender, receiver, is_read in messages:
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                is_read=is_read
            )
            if is_read:
                message.read_at = timezone.now()
                message.save()
            created_count += 1
        
        # Create some threaded conversations
        root_message = Message.objects.create(
            sender=user1,
            receiver=user2,
            content="Let's discuss the new project requirements."
        )
        
        # Add replies
        reply1 = Message.objects.create(
            sender=user2,
            receiver=user1,
            content="Great idea! I have some thoughts on the timeline.",
            parent_message=root_message,
            is_read=False
        )
        
        Message.objects.create(
            sender=user1,
            receiver=user2,
            content="What's your proposed timeline?",
            parent_message=reply1,
            is_read=False
        )
        
        self.stdout.write(f"✅ Created {created_count + 3} test messages with threading")
