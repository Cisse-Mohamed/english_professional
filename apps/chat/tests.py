from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Thread, Message, MessageReadReceipt

User = get_user_model()

class ChatModelsTest(TestCase):
    def setUp(self):
        """Set up users and a chat thread for tests."""
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')
        
        # A thread between user1 and user2
        self.thread1 = Thread.objects.create()
        self.thread1.participants.add(self.user1, self.user2)

        # A group chat thread with all three users
        self.group_thread = Thread.objects.create()
        self.group_thread.participants.add(self.user1, self.user2, self.user3)

    def test_message_creation(self):
        """Test that a message is created and associated with a thread."""
        message = Message.objects.create(
            thread=self.thread1,
            sender=self.user1,
            content='Hello, user2!'
        )
        self.assertEqual(self.thread1.messages.count(), 1)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Hello, user2!')

    def test_message_read_receipt(self):
        """Test the read receipt mechanism."""
        message = Message.objects.create(
            thread=self.thread1,
            sender=self.user1,
            content='This is a test message.'
        )

        # Initially, the message should not be read by user2
        self.assertNotIn(self.user2, message.read_by.all())

        # Simulate user2 reading the message by creating a receipt
        MessageReadReceipt.objects.create(user=self.user2, message=message)

        # Now, the message should be in user2's read_messages
        self.assertIn(self.user2, message.read_by.all())
        self.assertIn(message, self.user2.read_messages.all())

    def test_group_chat_read_receipts(self):
        """Test that read receipts work independently in a group chat."""
        message = Message.objects.create(
            thread=self.group_thread,
            sender=self.user1,
            content='Hello, group!'
        )

        # The sender (user1) should not have a read receipt for their own message
        self.assertNotIn(self.user1, message.read_by.all())

        # Neither of the other participants should have read it yet
        self.assertNotIn(self.user2, message.read_by.all())
        self.assertNotIn(self.user3, message.read_by.all())

        # Simulate user2 reading the message
        MessageReadReceipt.objects.create(user=self.user2, message=message)
        
        # Check status: user2 has read, user3 has not
        self.assertIn(self.user2, message.read_by.all())
        self.assertNotIn(self.user3, message.read_by.all())

        # Simulate user3 reading the message
        MessageReadReceipt.objects.create(user=self.user3, message=message)
        
        # Check status: both have read
        self.assertIn(self.user2, message.read_by.all())
        self.assertIn(self.user3, message.read_by.all())
        self.assertEqual(message.read_by.count(), 2)

    def test_unread_message_query(self):
        """Test a query to find unread messages for a user."""
        # user1 sends two messages
        msg1 = Message.objects.create(thread=self.group_thread, sender=self.user1, content='First message')
        msg2 = Message.objects.create(thread=self.group_thread, sender=self.user1, content='Second message')
        
        # user2 sends one message
        Message.objects.create(thread=self.group_thread, sender=self.user2, content='Reply from user2')

        # Simulate user3 reading the first message from user1
        MessageReadReceipt.objects.create(user=self.user3, message=msg1)

        # Query for all messages in the thread that user3 has not read and did not send
        unread_for_user3 = Message.objects.filter(
            thread=self.group_thread
        ).exclude(
            sender=self.user3
        ).exclude(
            read_receipts__user=self.user3
        )
        
        self.assertEqual(unread_for_user3.count(), 2)
        # The unread messages should be msg2 (from user1) and the message from user2
        self.assertIn(msg2, unread_for_user3)
        self.assertNotIn(msg1, unread_for_user3)