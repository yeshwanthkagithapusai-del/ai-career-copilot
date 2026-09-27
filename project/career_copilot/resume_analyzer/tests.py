from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Resume


class ResumeAnalyzerViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.resume = Resume.objects.create(
            user=self.user,
            target_role='Data Analyst',
            job_description='Analyze data',
            analysis_data={
                'overall_score': 85,
                'category_scores': {'communication_skills': 90},
                'skills_found': ['Python'],
                'missing_skills': [],
                'strong_sections': ['Summary'],
                'weak_sections': [],
                'matched_keywords': ['Python'],
                'suggestions': ['Add more metrics'],
                'ai_suggestions': [],
            },
        )

    def test_ats_report_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/resume/report/{self.resume.id}/')
        self.assertEqual(response.status_code, 200)
