from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Course, Lesson, LessonProgress, Assignment, Submission

User = get_user_model()

class CourseModelsTest(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.instructor = User.objects.create_user(
            username='instructor', 
            email='instructor@test.com', 
            password='password', 
            is_instructor=True
        )
        self.student = User.objects.create_user(
            username='student', 
            email='student@test.com', 
            password='password'
        )
        self.course = Course.objects.create(
            title='Test Course', 
            description='A course for testing.', 
            instructor=self.instructor
        )
        self.lesson = Lesson.objects.create(
            course=self.course, 
            title='Test Lesson', 
            content='Lesson content.'
        )

    def test_lesson_progress_completion_timestamp(self):
        """
        Test that `completed_at` is set only when `is_completed` is first set to True.
        """
        # Create a new lesson progress, it should not be completed.
        progress = LessonProgress.objects.create(
            student=self.student,
            lesson=self.lesson
        )
        self.assertFalse(progress.is_completed)
        self.assertIsNone(progress.completed_at)

        # Mark as complete and save.
        progress.is_completed = True
        progress.save()
        progress.refresh_from_db()

        # Check that completed_at is now set.
        self.assertTrue(progress.is_completed)
        self.assertIsNotNone(progress.completed_at)
        
        # Store the timestamp.
        first_completion_time = progress.completed_at

        # Save the object again without changes. The timestamp should not change.
        progress.save()
        progress.refresh_from_db()
        self.assertEqual(progress.completed_at, first_completion_time)

        # Un-completing and re-completing should not change the original completion time.
        progress.is_completed = False
        progress.save()
        progress.is_completed = True
        progress.save()
        progress.refresh_from_db()
        self.assertEqual(progress.completed_at, first_completion_time)