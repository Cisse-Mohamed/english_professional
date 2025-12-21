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

@shared_task
def check_assignment_deadlines():
    """
    Periodic task to check for upcoming assignment deadlines and send notifications.
    """
    # Logic to query assignments nearing deadline would go here.
    # Example: assignments = Assignment.objects.filter(deadline__lte=timezone.now() + timedelta(days=1))
    # For each assignment, trigger send_email_notification
    return "Checked assignment deadlines."

@shared_task
def send_message_notification(recipient_email, sender_name, message_preview):
    """
    Task to send an email notification for a new chat message.
    """
    subject = f"New message from {sender_name}"
    message = f"You have received a new message from {sender_name}:\n\n{message_preview}\n\nLog in to reply."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )
    return f"Message notification sent to {recipient_email}"