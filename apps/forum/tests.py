from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.courses.models import Course # Assuming Course model is needed for context
from .models import DiscussionThread, DiscussionPost # Assuming these models are needed for context

User = get_user_model()

class ChatbotQueryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.course = Course.objects.create(title='Test Course', description='A course for testing')
        self.thread = DiscussionThread.objects.create(
            title='Test Thread',
            content='This is the content of the test thread.',
            author=self.user,
            course=self.course
        )
        DiscussionPost.objects.create(
            thread=self.thread,
            author=self.user,
            content='This is a test post content.'
        )
        self.chatbot_query_url = reverse('forum:chatbot_query')

    def test_chatbot_query_post_success(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.chatbot_query_url, {
            'message': 'Hello chatbot',
            'thread_title': self.thread.title,
            'thread_content': self.thread.content,
            'posts_content': 'This is a test post content.'
        }, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Hello there! How can I assist you with this thread?'})

    def test_chatbot_query_get_method_not_allowed(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.chatbot_query_url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid request method'})

    def test_chatbot_query_unauthenticated(self):
        response = self.client.post(self.chatbot_query_url, {
            'message': 'Hello chatbot',
            'thread_title': self.thread.title,
            'thread_content': self.thread.content,
            'posts_content': 'This is a test post content.'
        }, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302) # Should redirect to login
        self.assertIn('/accounts/login/?next=', response.url)

    def test_chatbot_query_simulated_summary_response(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.chatbot_query_url, {
            'message': 'Summarize the thread',
            'thread_title': self.thread.title,
            'thread_content': self.thread.content,
            'posts_content': 'This is a test post content.'
        }, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertIn('AI Simulation: This thread, titled', json_response['response'])
        self.assertIn(self.thread.title, json_response['response'])