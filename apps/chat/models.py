from django.db import models
from django.conf import settings

class Thread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.id}"

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
    is_read = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['thread', '-timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"


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
    
    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to message {self.message.id}"