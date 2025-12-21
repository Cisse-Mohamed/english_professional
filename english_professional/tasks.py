from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import time

@shared_task
def send_email_notification(subject, message, recipient_list):
    """
    Background task to send email notifications.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
    return f"Email sent to {len(recipient_list)} recipients."

@shared_task
def generate_system_report():
    """
    Background task to generate system reports.
    """
    # Simulate report generation time
    time.sleep(5)
    return f"System report generated at {timezone.now()}"