from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.forum.models import Post
from apps.chat.models import Message
from .moderation import contains_inappropriate_content

@receiver(pre_save, sender=Post)
def flag_inappropriate_post(sender, instance, **kwargs):
    # Check title and content for inappropriate words
    if contains_inappropriate_content(instance.title) or contains_inappropriate_content(instance.content):
        # Ensure the model has the is_flagged field
        if hasattr(instance, 'is_flagged'):
            instance.is_flagged = True

@receiver(pre_save, sender=Message)
def flag_inappropriate_message(sender, instance, **kwargs):
    if contains_inappropriate_content(instance.content):
        if hasattr(instance, 'is_flagged'):
            instance.is_flagged = True