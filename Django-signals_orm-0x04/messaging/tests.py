from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

# Get the active User model
User = get_user_model()


class SignalTestCase(TestCase):
    """
    Test suite to verify that Django signals are working correctly.
    Tests for Task 0: Notification creation on new message.
    """

    def setUp(self):
        """Set up two users for testing purposes before each test."""
        self.user_sender = User.objects.create_user(
            username='sender',
            password='password123'
        )
        self.user_receiver = User.objects.create_user(
            username='receiver',
            password='password123'
        )

    def test_notification_is_created_when_new_message_is_saved(self):
        """
        Tests that a Notification is automatically created via a post_save signal
        when a new Message instance is created and saved.
        """
        # 1. Verify that no notifications exist at the start of the test.
        self.assertEqual(Notification.objects.count(), 0)
        
        # 2. Create a new message. This action should trigger the post_save signal.
        message = Message.objects.create(
            sender=self.user_sender,
            receiver=self.user_receiver,
            content="Hello, this is a test message!"
        )
        
        # 3. Verify that exactly one notification has been created in the database.
        self.assertEqual(Notification.objects.count(), 1)
        
        # 4. Verify that the created notification is correct.
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user_receiver)  # It's for the receiver.
        self.assertEqual(notification.message, message)  # It's linked to the correct message.
        self.assertFalse(notification.is_read)  # It should be unread by default.


class MessageEditTestCase(TestCase):
    """
    Test suite for Task 1: Message edit logging.
    """

    def setUp(self):
        """Set up users and a message for testing."""
        self.user_sender = User.objects.create_user(
            username='sender',
            password='password123'
        )
        self.user_receiver = User.objects.create_user(
            username='receiver',
            password='password123'
        )
        self.message = Message.objects.create(
            sender=self.user_sender,
            receiver=self.user_receiver,
            content="Original content"
        )

    def test_message_history_is_created_on_edit(self):
        """
        Tests that MessageHistory is created when a message is edited.
        """
        # Initially, no history should exist
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(self.message.edited)
        
        # Edit the message
        self.message.content = "Edited content"
        self.message.save()
        
        # Verify history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.message, self.message)
        
        # Verify edited flag is set
        self.message.refresh_from_db()
        self.assertTrue(self.message.edited)


class UserDeletionTestCase(TestCase):
    """
    Test suite for Task 2: User deletion cleanup.
    """

    def setUp(self):
        """Set up users and related data for testing."""
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )
        # Create messages
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1"
        )
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 2"
        )
        # Create notification
        self.notification = Notification.objects.create(
            user=self.user2,
            message=self.message1
        )

    def test_user_deletion_cleans_up_related_data(self):
        """
        Tests that deleting a user cleans up all related messages and notifications.
        """
        # Verify data exists
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 1)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Verify messages sent by user1 are deleted
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 0)
        # Verify messages received by user1 are deleted
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 0)
        
        # Delete user2
        self.user2.delete()
        
        # Verify notification is deleted
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 0)


class ThreadedConversationTestCase(TestCase):
    """
    Test suite for Task 3: Threaded conversations.
    """

    def setUp(self):
        """Set up users and threaded messages for testing."""
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )
        # Create parent message
        self.parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        # Create reply
        self.reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=self.parent_message
        )

    def test_threaded_conversation_structure(self):
        """Tests that threaded conversations work correctly."""
        # Verify parent message has no parent
        self.assertIsNone(self.parent_message.parent_message)
        
        # Verify reply has parent
        self.assertEqual(self.reply.parent_message, self.parent_message)
        
        # Verify reverse relation works
        replies = self.parent_message.replies.all()
        self.assertEqual(replies.count(), 1)
        self.assertEqual(replies.first(), self.reply)


class UnreadMessagesTestCase(TestCase):
    """
    Test suite for Task 4: Unread messages custom manager.
    """

    def setUp(self):
        """Set up users and messages for testing."""
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )
        # Create read message
        self.read_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            is_read=True
        )
        # Create unread message
        self.unread_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message",
            is_read=False
        )

    def test_unread_messages_manager(self):
        """Tests that the custom manager filters unread messages correctly."""
        unread_messages = Message.unread.unread_for_user(self.user2)
        
        # Should only return unread messages
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first(), self.unread_message)
        self.assertFalse(unread_messages.first().is_read)
