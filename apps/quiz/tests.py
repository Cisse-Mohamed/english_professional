from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Lesson
from .models import Quiz, Question, Choice, QuizSubmission
from django.utils import timezone
import datetime

User = get_user_model()

class TimedQuizTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.question_bank = QuestionBank.objects.create(course=self.course, title='Test Bank')
        self.quiz = Quiz.objects.create(course=self.course, question_bank=self.question_bank, title='Test Quiz', duration=1, number_of_questions=1)
        self.question = Question.objects.create(question_bank=self.question_bank, text='What is 1+1?')
        self.choice1 = Choice.objects.create(question=self.question, text='2', is_correct=True)
        self.choice2 = Choice.objects.create(question=self.question, text='3', is_correct=False)
        self.client.login(username='testuser', password='password')

    def test_start_quiz(self):
        """Test that a user can start a quiz."""
        response = self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        self.assertEqual(response.status_code, 302) # Redirects to quiz_detail
        self.assertTrue(QuizSubmission.objects.filter(student=self.user, quiz=self.quiz).exists())

    def test_quiz_in_progress(self):
        """Test that the timer is displayed during the quiz."""
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        response = self.client.get(reverse('quiz_detail', kwargs={'pk': self.quiz.pk}))
        self.assertContains(response, 'id="timer"')

    def test_submit_quiz(self):
        """Test that a user can submit a quiz."""
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        submission = QuizSubmission.objects.get(student=self.user, quiz=self.quiz)
        question = submission.questions.first()
        choice = question.choices.get(is_correct=True)
        response = self.client.post(reverse('quiz_take', kwargs={'pk': self.quiz.pk}), {f'question_{question.id}': choice.id})
        self.assertEqual(response.status_code, 302)
        submission.refresh_from_db()
        self.assertEqual(submission.score, 1)
        self.assertIsNotNone(submission.end_time)

    def test_auto_submit_on_time_up(self):
        """Test that the quiz is automatically submitted when the timer ends."""
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        submission = QuizSubmission.objects.get(student=self.user, quiz=self.quiz)
        submission.start_time = timezone.now() - datetime.timedelta(minutes=2)
        submission.save()
        
        question = submission.questions.first()
        choice = question.choices.get(is_correct=True)
        response = self.client.post(reverse('quiz_take', kwargs={'pk': self.quiz.pk}), {f'question_{question.id}': choice.id})

        submission.refresh_from_db()
        self.assertIsNotNone(submission.end_time)

    def test_view_quiz_result(self):
        """Test that a user can view the quiz result."""
        submission = QuizSubmission.objects.create(student=self.user, quiz=self.quiz, score=1, total_questions=1, end_time=timezone.now())
        response = self.client.get(reverse('quiz_detail', kwargs={'pk': self.quiz.pk}))
        self.assertContains(response, 'Result')
        self.assertContains(response, '1 / 1')

class QuestionBankTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.question_bank = QuestionBank.objects.create(course=self.course, title='Test Bank')
        for i in range(10):
            question = Question.objects.create(question_bank=self.question_bank, text=f'Question {i}')
            Choice.objects.create(question=question, text='Correct', is_correct=True)
            Choice.objects.create(question=question, text='Incorrect', is_correct=False)

        self.quiz = Quiz.objects.create(course=self.course, question_bank=self.question_bank, title='Test Quiz', number_of_questions=5)
        self.client.login(username='testuser', password='password')

    def test_start_quiz_with_question_bank(self):
        """Test that a quiz with a question bank serves random questions."""
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        submission1 = QuizSubmission.objects.get(student=self.user, quiz=self.quiz)
        questions1 = list(submission1.questions.all())

        # Create another user and start the same quiz
        user2 = User.objects.create_user(username='testuser2', password='password')
        self.client.login(username='testuser2', password='password')
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        submission2 = QuizSubmission.objects.get(student=user2, quiz=self.quiz)
        questions2 = list(submission2.questions.all())

        self.assertEqual(len(questions1), 5)
        self.assertEqual(len(questions2), 5)
        # Check if the questions are not the same for both users
        self.assertNotEqual(questions1, questions2)

    def test_quiz_submission_with_question_bank(self):
        """Test that a quiz submission with a question bank works correctly."""
        self.client.get(reverse('quiz_start', kwargs={'pk': self.quiz.pk}))
        submission = QuizSubmission.objects.get(student=self.user, quiz=self.quiz)
        
        # Answer all questions correctly
        post_data = {}
        for question in submission.questions.all():
            correct_choice = question.choices.get(is_correct=True)
            post_data[f'question_{question.id}'] = correct_choice.id

        response = self.client.post(reverse('quiz_take', kwargs={'pk': self.quiz.pk}), post_data)
        self.assertEqual(response.status_code, 302)

        submission.refresh_from_db()
        self.assertEqual(submission.score, 5)
        self.assertEqual(submission.total_questions, 5)


