from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Test


class TestAnalysisViewTests(TestCase):
    def test_anonymous_user_cannot_view_completed_test_analysis(self):
        user = get_user_model().objects.create_user(
            username='demo-user',
            email='demo@example.com',
            password='demo-password123',
        )
        test = Test.objects.create(
            user=user,
            skill='Python',
            difficulty='beginner',
            num_questions=5,
            completed=True,
            score=80,
            accuracy=80,
            correct_count=4,
            wrong_count=1,
            time_taken=120,
            topic_performance={'Python': {'accuracy': 80, 'correct': 4, 'total': 5}},
            strong_topics=[('Python', 80)],
            weak_topics=[('SQL', 40)],
            suggestions=['Keep practicing'],
        )

        response = self.client.get(reverse('assessments:test_analysis', kwargs={'test_id': test.id}))

        # Since it now requires login, anonymous should redirect
        self.assertEqual(response.status_code, 302)
