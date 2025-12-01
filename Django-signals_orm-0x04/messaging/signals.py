from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


# Task 0: Signal to create notification when a new message is created
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Creates a Notification for the receiver when a new Message is created.
    This is triggered automatically via post_save signal.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


# Task 1: Signal to log message edits before saving
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before a Message is saved, check if it's an update and if the content
    has changed. If so, log the old content to the MessageHistory model.
    """
    if instance.pk:  # Only run for existing messages (updates)
        try:
            original = Message.objects.get(pk=instance.pk)
            if original.content != instance.content:
                # Log the old content before the update
                MessageHistory.objects.create(
                    message=original,
                    old_content=original.content
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass  # This is a new message, do nothing


# Task 2: Signal to clean up related data when a user is deleted
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    This signal handler is triggered after a User instance is deleted.
    It cleans up all messages, notifications, and message histories
    associated with the user.
    
    Note: While CASCADE on ForeignKey handles most of this automatically,
    this signal ensures explicit cleanup and can handle edge cases.
    """
    user_id = instance.id
    
    # Delete messages sent by the user
    Message.objects.filter(sender=user_id).delete()
    
    # Delete messages received by the user
    Message.objects.filter(receiver=user_id).delete()
    
    # Delete notifications for the user
    Notification.objects.filter(user=user_id).delete()
    
    # Delete message histories for messages that belonged to this user
    # (This will be handled by CASCADE, but we can be explicit)
    MessageHistory.objects.filter(message__sender=user_id).delete()
    MessageHistory.objects.filter(message__receiver=user_id).delete()
