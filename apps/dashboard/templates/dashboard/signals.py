from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from english_professional.tasks import send_email_notification

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        thread = instance.thread
        sender_user = instance.sender
        # Notify all participants except sender
        participants = thread.participants.exclude(id=sender_user.id)
        
        recipient_list = [p.email for p in participants if p.email]
        
        if recipient_list:
            subject = f"New Message from {sender_user.username}"
            message = f"You have received a new message in your chat.\n\n{instance.content[:50]}..."
            send_email_notification.delay(subject, message, recipient_list)