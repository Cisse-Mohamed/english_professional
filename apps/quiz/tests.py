from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.courses.models import Course
from .models import Quiz, Question, Choice, QuizSubmission, QuestionBank, QuizQuestionAttempt

User = get_user_model()

class QuizAppTests(TestCase):
    def setUp(self):
        """Set up the necessary objects for the test suite."""
        # Create users, one instructor, one student
        self.instructor = User.objects.create_user(username='testinstructor', password='password', is_instructor=True)
        self.student = User.objects.create_user(username='teststudent', password='password')

        # Create a course and a question bank
        # Note: The original test used 'owner', but the model uses 'instructor'.
        self.course = Course.objects.create(title='Test Course')
        self.course.instructors.add(self.instructor)
        self.question_bank = QuestionBank.objects.create(course=self.course, title='Test Bank')

        # Create 10 questions in the bank for testing randomization
        for i in range(10):
            question = Question.objects.create(question_bank=self.question_bank, text=f'Question {i}')
            Choice.objects.create(question=question, text='Correct', is_correct=True)
            Choice.objects.create(question=question, text='Incorrect', is_correct=False)
        
        # Create a quiz that uses 5 of those questions
        self.quiz = Quiz.objects.create(
            course=self.course, 
            question_bank=self.question_bank, 
            title='Test Quiz', 
            number_of_questions=5
        )
        self.client.login(username='teststudent', password='password')

    def test_start_quiz_creates_submission_and_attempts(self):
        """Test that starting a quiz creates a submission and the correct number of question attempts."""
        response = self.client.get(reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk}))
        self.assertEqual(response.status_code, 302) # Should redirect to the detail view
        
        # Check that a submission was created
        self.assertTrue(QuizSubmission.objects.filter(student=self.student, quiz=self.quiz).exists())
        submission = QuizSubmission.objects.get(student=self.student, quiz=self.quiz)

        # Check that the correct number of attempts were created, matching the quiz's number_of_questions
        self.assertEqual(submission.question_attempts.count(), self.quiz.number_of_questions)
        self.assertEqual(submission.total_questions, self.quiz.number_of_questions)

    def test_submit_quiz_correctly(self):
        """Test that a user can submit a quiz and it is graded correctly."""
        # Start the quiz first to create the submission and attempts
        self.client.get(reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk}))
        submission = QuizSubmission.objects.get(student=self.student, quiz=self.quiz)
        
        # Prepare POST data to answer all questions correctly
        post_data = {}
        for attempt in submission.question_attempts.all():
            correct_choice = attempt.question.choices.get(is_correct=True)
            post_data[f'question_{attempt.question.id}'] = correct_choice.id

        # Submit the quiz
        response = self.client.post(reverse('quiz:quiz_take', kwargs={'pk': self.quiz.pk}), post_data)
        self.assertEqual(response.status_code, 302) # Should redirect

        # Refresh the submission from the DB and check the score
        submission.refresh_from_db()
        self.assertEqual(submission.mcq_score, self.quiz.number_of_questions)
        self.assertIsNotNone(submission.end_time)

    def test_quiz_questions_are_randomized(self):
        """Test that two different students get different sets of questions."""
        # Student 1 starts the quiz
        self.client.get(reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk}))
        submission1 = QuizSubmission.objects.get(student=self.student, quiz=self.quiz)
        questions1_ids = set(attempt.question.id for attempt in submission1.question_attempts.all())

        # Create and log in a second student
        student2 = User.objects.create_user(username='student2', password='password')
        self.client.login(username='student2', password='password')

        # Student 2 starts the same quiz
        self.client.get(reverse('quiz:quiz_start', kwargs={'pk': self.quiz.pk}))
        submission2 = QuizSubmission.objects.get(student=student2, quiz=self.quiz)
        questions2_ids = set(attempt.question.id for attempt in submission2.question_attempts.all())

        self.assertEqual(len(questions1_ids), self.quiz.number_of_questions)
        self.assertEqual(len(questions2_ids), self.quiz.number_of_questions)
        # With 10 questions available and choosing 5, the chance of getting the exact same set is low.
        # This is a reasonable check for randomization.
        self.assertNotEqual(questions1_ids, questions2_ids)

    def test_view_quiz_result_after_submission(self):
        """Test that a user can view their quiz result after completing it."""
        # Manually create a completed submission for simplicity
        submission = QuizSubmission.objects.create(
            student=self.student, 
            quiz=self.quiz, 
            score=3, 
            total_questions=5, 
        )
        submission.end_time = timezone.now()
        submission.save()

        response = self.client.get(reverse('quiz:quiz_detail', kwargs={'pk': self.quiz.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Result')
        self.assertContains(response, '3 / 5')

    def test_instructor_can_view_essay_submissions(self):
        """Test that the course instructor can access the essay grading page."""
        self.client.logout()
        self.client.login(username='testinstructor', password='password')
        response = self.client.get(reverse('quiz:quiz_essay_submissions', kwargs={'pk': self.quiz.pk}))
        # This test requires a URL named 'quiz_essay_submissions', let's assume it exists.
        # If it doesn't, this test will fail and highlight the need for that URL.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Grade Essay Questions')