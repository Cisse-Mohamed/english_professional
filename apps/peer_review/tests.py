from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Lesson
from .models import PeerReviewAssignment, PeerReviewSubmission, PeerReviewReview
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class PeerReviewTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='password', is_instructor=True)
        self.student1 = User.objects.create_user(username='student1', password='password')
        self.student2 = User.objects.create_user(username='student2', password='password')
        self.course = Course.objects.create(title='Test Course', owner=self.instructor)
        self.lesson = Lesson.objects.create(course=self.course, title='Test Lesson', content='Test content')
        self.assignment = PeerReviewAssignment.objects.create(
            lesson=self.lesson,
            title='Test Peer Review Assignment',
            description='Test description',
            due_date='2025-12-31 23:59:59'
        )

    def test_create_assignment(self):
        """Test that an instructor can create a peer review assignment."""
        self.client.login(username='instructor', password='password')
        response = self.client.post(
            reverse('peer_review:assignment_create', kwargs={'lesson_pk': self.lesson.pk}),
            {'title': 'New Assignment', 'description': 'New description', 'due_date': '2026-01-01 12:00:00'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PeerReviewAssignment.objects.filter(title='New Assignment').exists())

    def test_submit_assignment(self):
        """Test that a student can submit a peer review assignment."""
        self.client.login(username='student1', password='password')
        submission_file = SimpleUploadedFile("file.txt", b"file_content")
        response = self.client.post(
            reverse('peer_review:submission_create', kwargs={'assignment_pk': self.assignment.pk}),
            {'submission_file': submission_file}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PeerReviewSubmission.objects.filter(student=self.student1, assignment=self.assignment).exists())

    def test_review_submission(self):
        """Test that a student can review a peer's submission."""
        self.client.login(username='student2', password='password')
        submission = PeerReviewSubmission.objects.create(assignment=self.assignment, student=self.student1)
        response = self.client.post(
            reverse('peer_review:review_create', kwargs={'submission_pk': submission.pk}),
            {'score': 90, 'comments': 'Good work!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PeerReviewReview.objects.filter(submission=submission, reviewer=self.student2).exists())

    def test_view_reviews(self):
        """Test that a student can see the reviews on their submission."""
        self.client.login(username='student1', password='password')
        submission = PeerReviewSubmission.objects.create(assignment=self.assignment, student=self.student1)
        PeerReviewReview.objects.create(submission=submission, reviewer=self.student2, score=90, comments='Good work!')
        response = self.client.get(reverse('peer_review:assignment_detail', kwargs={'pk': self.assignment.pk}))
        self.assertContains(response, 'Reviews on Your Submission')
        self.assertContains(response, 'Good work!')

