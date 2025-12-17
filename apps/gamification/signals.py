from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.courses.models import LessonProgress
from .models import UserPoints
from .utils import check_badges

@receiver(post_save, sender=LessonProgress)
def award_points_for_lesson(sender, instance, created, **kwargs):
    if instance.is_completed:
        # Get or create UserPoints
        user_points, _ = UserPoints.objects.get_or_create(user=instance.student)
        
        # Award 10 points for a lesson
        # To avoid double counting, we might want to track if points were already awarded for this specific progress
        # But for simplicity, we'll just add it.
        
        user_points.total_points += 10
        user_points.save()
        
        check_badges(instance.student)
