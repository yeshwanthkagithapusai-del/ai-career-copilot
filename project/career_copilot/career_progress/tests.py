from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import CareerProgress


class CareerProgressViewTests(TestCase):
    def test_anonymous_user_can_view_progress_page(self):
        user = get_user_model().objects.create_user(
            username='demo-user',
            email='demo@example.com',
            password='demo-password123',
        )
        CareerProgress.objects.create(user=user, metric_type='ats_score', score=70, previous_score=60)
        CareerProgress.objects.create(user=user, metric_type='test_score', score=80, previous_score=70)

        response = self.client.get(reverse('career_progress:career_progress'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Career Progress')
        self.assertContains(response, 'Overall Career Progress')
