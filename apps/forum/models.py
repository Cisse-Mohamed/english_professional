from django.db import models
from django.conf import settings
from apps.courses.models import Course

class DiscussionThread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forum_threads')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_threads')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Mentions
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in_threads', blank=True)
    
    # Metadata
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['course', '-updated_at']),
        ]

    def __str__(self):
        return self.title

class DiscussionPost(models.Model):
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    
    # Mentions
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in_posts', blank=True)
    
    # Metadata
    is_solution = models.BooleanField(default=False, help_text="Marked as solution by thread author or instructor")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
        ]

    def __str__(self):
        return f"Post by {self.author} in {self.thread}"


class ForumReaction(models.Model):
    """Emoji reactions to forum posts"""
    REACTION_TARGET_CHOICES = [
        ('thread', 'Thread'),
        ('post', 'Post'),
    ]
    
    target_type = models.CharField(max_length=10, choices=REACTION_TARGET_CHOICES)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_reactions')
    emoji = models.CharField(max_length=10, help_text="Emoji character or code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['target_type', 'thread', 'emoji']),
            models.Index(fields=['target_type', 'post', 'emoji']),
        ]
    
    def __str__(self):
        target = self.thread if self.target_type == 'thread' else self.post
        return f"{self.user.username} reacted {self.emoji} to {target}"