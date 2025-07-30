"""
Django signals for the messaging app.

This module contains signal handlers that automatically create notifications
when certain events occur, such as when a new message is created.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, Notification, UserProfile


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


# Import Q for complex queries
from django.db import models
