from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import InterviewSession, InterviewAnswer


class InterviewViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

    def test_interview_room_renders_valid_timer_script(self):
        self.client.force_login(self.user)
        interview = InterviewSession.objects.create(
            user=self.user,
            target_role='Software Engineer',
            interview_type='technical',
            difficulty='intermediate',
            num_questions=1,
        )
        InterviewAnswer.objects.create(interview=interview, question='Test question')

        response = self.client.get(f'/interviews/room/{interview.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("document.getElementById(\"timer\").textContent = mins + \":\" + String(secs).padStart(2, \"0\");", response.content.decode())
