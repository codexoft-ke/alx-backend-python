"""
Django signals for the messaging app.

This module contains signal handlers that automatically create notifications
when certain events occur, such as when a new message is created.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from .models import Message, Notification, UserProfile, MessageHistory


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler that logs message edits by storing the old content in MessageHistory.
    
    This function is triggered before a Message instance is saved.
    If it's an existing message being updated with different content,
    it creates a MessageHistory entry with the old content.
    
    Args:
        sender: The model class (Message)
        instance: The actual Message instance being saved
        **kwargs: Additional keyword arguments
    """
    # Only proceed if this is an update (not a new message)
    if instance.pk:
        try:
            # Get the existing message from database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if the content has actually changed
            if old_message.content != instance.content:
                # Get the next version number for this message
                last_version = MessageHistory.objects.filter(message=instance).aggregate(
                    max_version=models.Max('version')
                )['max_version'] or 0
                
                # Store the old content in MessageHistory
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender,  # Assuming sender is doing the edit
                    version=last_version + 1
                )
                
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
                
                print(f"✅ Message edit logged: Message #{instance.pk} content changed")
                
                # Create notification for the receiver about the edit
                if hasattr(instance, 'receiver'):
                    notification_title = f"Message edited by {instance.sender.username}"
                    notification_description = f"A message from {instance.sender.username} was edited"
                    
                    Notification.objects.create(
                        user=instance.receiver,
                        message=instance,
                        notification_type='message_edited',
                        title=notification_title,
                        description=notification_description
                    )
                    
                    print(f"✅ Edit notification created for {instance.receiver.username}")
                
        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass
        except Exception as e:
            print(f"❌ Error in message edit logging: {e}")


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.
    
    This function is triggered automatically when a Message instance is saved.
    If it's a new message (created=True), it creates a notification for the receiver.
    
    Args:
        sender: The model class (Message)
        instance: The actual Message instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        # Create notification for the message receiver
        notification_title = f"New message from {instance.sender.username}"
        notification_description = f"You have received a new message: {instance.content[:50]}{'...' if len(instance.content) > 50 else ''}"
        
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='new_message',
            title=notification_title,
            description=notification_description
        )
        
        print(f"✅ Notification created for {instance.receiver.username} about message from {instance.sender.username}")


@receiver(post_save, sender=Message)
def message_read_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a message is marked as read.
    
    This function is triggered when a Message instance is updated.
    If the message was marked as read, it creates a notification for the sender.
    
    Args:
        sender: The model class (Message)
        instance: The actual Message instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created and instance.is_read:
        # Check if there's already a read notification for this message
        existing_notification = Notification.objects.filter(
            user=instance.sender,
            message=instance,
            notification_type='message_read'
        ).exists()
        
        if not existing_notification:
            notification_title = f"Message read by {instance.receiver.username}"
            notification_description = f"Your message has been read: {instance.content[:50]}{'...' if len(instance.content) > 50 else ''}"
            
            Notification.objects.create(
                user=instance.sender,
                message=instance,
                notification_type='message_read',
                title=notification_title,
                description=notification_description
            )
            
            print(f"✅ Read notification created for {instance.sender.username}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler that creates a UserProfile when a new User is created.
    
    Args:
        sender: The model class (User)
        instance: The actual User instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        UserProfile.objects.create(user=instance)
        print(f"✅ User profile created for {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler that saves the UserProfile when User is saved.
    
    Args:
        sender: The model class (User)
        instance: The actual User instance that was saved
        **kwargs: Additional keyword arguments
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=UserProfile)
def user_status_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates notifications when user status changes.
    
    This creates notifications for friends/contacts when a user comes online or goes offline.
    
    Args:
        sender: The model class (UserProfile)
        instance: The actual UserProfile instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created:  # Only for updates, not new profiles
        # Get users who have messaged with this user (simple friend detection)
        related_users = User.objects.filter(
            models.Q(sent_messages__receiver=instance.user) |
            models.Q(received_messages__sender=instance.user)
        ).distinct().exclude(id=instance.user.id)
        
        # Create notifications for status changes
        if instance.is_online:
            notification_type = 'user_online'
            title = f"{instance.user.username} is now online"
            description = f"{instance.user.username} came online"
        else:
            notification_type = 'user_offline'
            title = f"{instance.user.username} went offline"
            description = f"{instance.user.username} is now offline"
        
        # Create notifications for related users (limit to avoid spam)
        for user in related_users[:10]:  # Limit to 10 most recent contacts
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                description=description
            )


@receiver(post_delete, sender=Message)
def message_deleted_notification(sender, instance, **kwargs):
    """
    Signal handler that creates a notification when a message is deleted.
    
    Args:
        sender: The model class (Message)
        instance: The Message instance that was deleted
        **kwargs: Additional keyword arguments
    """
    # Notify the receiver that a message was deleted
    notification_title = f"Message deleted by {instance.sender.username}"
    notification_description = f"A message from {instance.sender.username} was deleted"
    
    Notification.objects.create(
        user=instance.receiver,
        notification_type='new_message',  # Using new_message type for simplicity
        title=notification_title,
        description=notification_description
    )
    
    print(f"✅ Deletion notification created for {instance.receiver.username}")


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler that cleans up all user-related data when a user is deleted.
    
    This function is triggered automatically when a User instance is deleted.
    It ensures all related data is properly cleaned up, respecting foreign key constraints.
    
    Args:
        sender: The model class (User)
        instance: The User instance that was deleted
        **kwargs: Additional keyword arguments
    """
    username = instance.username
    print(f"🧹 Starting cleanup for deleted user: {username}")
    
    try:
        # Track counts for logging
        cleanup_stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'notifications': 0,
            'message_history': 0,
            'user_profile': 0
        }
        
        # Clean up messages sent by this user
        sent_messages = Message.objects.filter(sender=instance)
        cleanup_stats['messages_sent'] = sent_messages.count()
        if cleanup_stats['messages_sent'] > 0:
            # Delete message histories first (foreign key constraint)
            for message in sent_messages:
                MessageHistory.objects.filter(message=message).delete()
            sent_messages.delete()
            print(f"   ✅ Deleted {cleanup_stats['messages_sent']} sent messages")
        
        # Clean up messages received by this user
        received_messages = Message.objects.filter(receiver=instance)
        cleanup_stats['messages_received'] = received_messages.count()
        if cleanup_stats['messages_received'] > 0:
            # Delete message histories first (foreign key constraint)
            for message in received_messages:
                MessageHistory.objects.filter(message=message).delete()
            received_messages.delete()
            print(f"   ✅ Deleted {cleanup_stats['messages_received']} received messages")
        
        # Clean up notifications for this user
        user_notifications = Notification.objects.filter(user=instance)
        cleanup_stats['notifications'] = user_notifications.count()
        if cleanup_stats['notifications'] > 0:
            user_notifications.delete()
            print(f"   ✅ Deleted {cleanup_stats['notifications']} notifications")
        
        # Clean up message edit history by this user
        user_message_edits = MessageHistory.objects.filter(edited_by=instance)
        cleanup_stats['message_history'] = user_message_edits.count()
        if cleanup_stats['message_history'] > 0:
            user_message_edits.delete()
            print(f"   ✅ Deleted {cleanup_stats['message_history']} message edit entries")
        
        # Clean up user profile (this should be handled by CASCADE, but let's be explicit)
        try:
            if hasattr(instance, 'profile'):
                instance.profile.delete()
                cleanup_stats['user_profile'] = 1
                print(f"   ✅ Deleted user profile")
        except UserProfile.DoesNotExist:
            pass  # Profile might not exist or already deleted by CASCADE
        
        # Log summary
        total_items = sum(cleanup_stats.values())
        print(f"🎉 User cleanup completed for '{username}': {total_items} items deleted")
        print(f"   📊 Breakdown: {cleanup_stats}")
        
        # Create a system notification for admins (if there's an admin user)
        try:
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='user_offline',  # Reusing existing type
                    title=f'User Account Deleted: {username}',
                    description=f'User "{username}" deleted their account. {total_items} related data items were cleaned up.'
                )
        except Exception as e:
            print(f"   ⚠️ Could not create admin notification: {e}")
            
    except Exception as e:
        print(f"❌ Error during user data cleanup for '{username}': {e}")
        # Don't raise the exception to avoid preventing user deletion
        # Log the error for debugging purposes


# Import Q for complex queries
from django.db import models
