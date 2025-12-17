from django.db import models
from apps.courses.models import Course

class VideoSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='video_sessions')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_url = models.URLField(blank=True, help_text="Link to external meeting or internal room name")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
