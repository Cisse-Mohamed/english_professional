from django.db import models
from django.conf import settings
from apps.courses.models import Lesson

class PeerReviewAssignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='peer_review_assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title

class PeerReviewSubmission(models.Model):
    assignment = models.ForeignKey(PeerReviewAssignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='peer_review_submissions')
    submission_file = models.FileField(upload_to='peer_review/submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"

class PeerReviewReview(models.Model):
    submission = models.ForeignKey(PeerReviewSubmission, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='peer_reviews')
    score = models.PositiveIntegerField()
    comments = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('submission', 'reviewer')
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.submission.student.username}'s submission"
