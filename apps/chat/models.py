from django.db import models
from django.conf import settings
from django.utils import timezone

class Thread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.id}"

    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    
    # Media files
    audio_file = models.FileField(upload_to='chat/audio/', blank=True, null=True)
    video_file = models.FileField(upload_to='chat/video/', blank=True, null=True)
    
    # Translation support
    original_language = models.CharField(max_length=10, blank=True, null=True, help_text="ISO language code")
    translated_content = models.JSONField(default=dict, blank=True, help_text="Translations: {lang_code: translated_text}")
    
    # Mentions
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in_messages', blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # New field for read receipts
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MessageReadReceipt', related_name='read_messages', blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['thread', '-timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"


class MessageReadReceipt(models.Model):
    """Tracks when a user has read a message."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'message')
        indexes = [
            models.Index(fields=['user', 'message']),
        ]
        ordering = ['-read_at']

    def __str__(self):
        return f"User {self.user.id} read message {self.message.id} at {self.read_at}"


class MessageReaction(models.Model):
    """Emoji reactions to messages"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reactions')
    emoji = models.CharField(max_length=10, help_text="Emoji character or code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user', 'emoji')
        indexes = [
            models.Index(fields=['message', 'emoji']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to message {self.message.id}"