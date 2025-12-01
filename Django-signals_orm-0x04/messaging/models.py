from django.db import models
from django.conf import settings
from .managers import UnreadMessagesManager


class Message(models.Model):
    """
    Represents a direct message from one user to another.
    Includes fields for threading, read status, and edit tracking.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # Field for Task 1: Track if message has been edited
    edited = models.BooleanField(default=False)
    # Field for Task 4: Track if message has been read
    is_read = models.BooleanField(default=False)
    # Field for Task 3: Self-referential foreign key for threaded conversations
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    # Default manager
    objects = models.Manager()
    # Custom manager for Task 4: Unread messages
    unread = UnreadMessagesManager()

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    class Meta:
        ordering = ['-timestamp']


class Notification(models.Model):
    """
    Represents a notification for a user about a new message.
    Created automatically via post_save signal when a new Message is created.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='message_notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} about message {self.message.id}"

    class Meta:
        ordering = ['-created_at']


class MessageHistory(models.Model):
    """
    Logs the previous content of a message every time it is edited.
    Created automatically via pre_save signal before a message is updated.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message History"

    def __str__(self):
        return f"Edit for message {self.message.id} at {self.edited_at}"
