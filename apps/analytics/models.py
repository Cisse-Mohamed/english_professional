from django.db import models
from django.conf import settings
from apps.courses.models import Course
from django.utils import timezone


class StudentPerformanceSnapshot(models.Model):
    """Periodic snapshot of student performance for trend analysis"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_snapshots')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='performance_snapshots')
    
    # Metrics
    quiz_average = models.FloatField(default=0.0, help_text="Average quiz score percentage")
    assignment_average = models.FloatField(default=0.0, help_text="Average assignment grade")
    completion_rate = models.FloatField(default=0.0, help_text="Percentage of lessons completed")
    engagement_score = models.FloatField(default=0.0, help_text="Overall engagement metric")
    
    # Metadata
    snapshot_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['student', 'course', '-snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.snapshot_date.date()})"


class CourseEngagementMetrics(models.Model):
    """Aggregated course engagement metrics for instructors"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='engagement_metrics')
    
    # Metrics
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0, help_text="Students active in last 7 days")
    average_completion_rate = models.FloatField(default=0.0)
    average_quiz_score = models.FloatField(default=0.0)
    forum_activity_count = models.IntegerField(default=0, help_text="Total forum posts/threads")
    dropout_risk_count = models.IntegerField(default=0, help_text="Students at risk of dropping out")
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['course', '-calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - Metrics ({self.calculated_at.date()})"


class StudentActivityLog(models.Model):
    """Log student activities for engagement tracking"""
    ACTIVITY_TYPES = [
        ('lesson_view', 'Lesson Viewed'),
        ('lesson_complete', 'Lesson Completed'),
        ('quiz_attempt', 'Quiz Attempted'),
        ('assignment_submit', 'Assignment Submitted'),
        ('forum_post', 'Forum Post Created'),
        ('chat_message', 'Chat Message Sent'),
        ('video_join', 'Video Session Joined'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    activity_data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['student', '-timestamp']),
            models.Index(fields=['course', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.get_activity_type_display()} ({self.timestamp})"