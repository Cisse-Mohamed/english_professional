from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.conf import settings
from .models import Announcement


@receiver(post_save, sender=Announcement)
def send_announcement_emails(sender, instance, created, **kwargs):
    """Send email notifications when announcement is created"""
    if created and instance.send_email:
        recipients = instance.get_recipients()
        
        if not recipients:
            return
        
        subject = f"[{instance.get_priority_display()}] {instance.title}"
        
        message = f"""
{instance.title}

{instance.content}

---
Posted by: {instance.author.get_full_name() or instance.author.username}
Priority: {instance.get_priority_display()}
Scope: {instance.get_scope_display()}
{f"Course: {instance.course.title}" if instance.course else ""}

View announcement: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/announcements/{instance.id}/
        """.strip()
        
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com'
        
        # Prepare mass email
        emails = []
        for recipient in recipients:
            if recipient.email:
                emails.append((
                    subject,
                    message,
                    from_email,
                    [recipient.email]
                ))
        
        # Send in batches to avoid overwhelming the email server
        if emails:
            try:
                send_mass_mail(emails, fail_silently=False)
            except Exception as e:
                # Log error but don't fail the announcement creation
                print(f"Error sending announcement emails: {e}")