from django.db import models
from apps.courses.models import Course
from django.conf import settings # Import settings to get AUTH_USER_MODEL
from django.utils import timezone # Import timezone
from django.utils.text import slugify

class InstantVideoSession(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='instant_video_sessions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{timezone.now().strftime('%Y%m%d%H%M%S')}")
            unique_slug = base_slug
            num = 1
            while InstantVideoSession.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class InstantVideoSessionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instant_video_session_participations')
    session = models.ForeignKey(InstantVideoSession, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_host = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'session')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} in Instant Session: {self.session.title}"


class VideoSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='video_sessions')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_url = models.CharField(max_length=100, unique=True, blank=True, help_text="Unique internal identifier for the video session.")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def save(self, *args, **kwargs):
        if not self.meeting_url:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while VideoSession.objects.filter(meeting_url=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.meeting_url = unique_slug
        super().save(*args, **kwargs)

class BreakoutRoom(models.Model):
    session = models.ForeignKey(VideoSession, on_delete=models.CASCADE, related_name='breakout_rooms')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('session', 'name') # A session cannot have two breakout rooms with the same name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug combining session ID and room name
            base_slug = slugify(f"{self.session.id}-{self.name}")
            unique_slug = base_slug
            num = 1
            while BreakoutRoom.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Breakout Room: {self.name} for {self.session.title}"

class VideoSessionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_session_participations')
    session = models.ForeignKey(VideoSession, on_delete=models.CASCADE, related_name='participants')
    breakout_room = models.ForeignKey(BreakoutRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_host = models.BooleanField(default=False) # To distinguish host from regular participants

    class Meta:
        unique_together = ('user', 'session') # A user can only participate once per session
        ordering = ['joined_at']

    def __str__(self):
        room_info = f" in {self.breakout_room.name}" if self.breakout_room else ""
        return f"{self.user.username} in {self.session.title}{room_info}"

class VideoRecording(models.Model):
    session = models.ForeignKey(VideoSession, on_delete=models.CASCADE, related_name='recordings')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    file_url = models.URLField(max_length=200, blank=True, null=True) # URL to the recorded file
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Recording for {self.session.title} by {self.recorded_by.username if self.recorded_by else 'N/A'}"

