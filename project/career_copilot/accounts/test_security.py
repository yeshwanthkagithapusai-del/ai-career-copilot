from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from resume_analyzer.models import Resume
from interviews.models import InterviewSession
from assessments.models import Test
from roadmaps.models import Roadmap
import json

User = get_user_model()

class SecurityTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1@example.com', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='user2@example.com', email='user2@example.com', password='password123')

        # Create objects for user1
        self.resume = Resume.objects.create(user=self.user1, target_role="Dev", ats_score=80)
        self.interview = InterviewSession.objects.create(user=self.user1, target_role="Dev")
        self.test_obj = Test.objects.create(user=self.user1, skill="Python", completed=True)
        self.roadmap = Roadmap.objects.create(user=self.user1, target_career="Cybersecurity Analyst")

    def test_unauthorized_resume_access(self):
        self.client.force_login(self.user2)
        response = self.client.get(f'/resume/report/{self.resume.id}/')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_interview_access(self):
        self.client.force_login(self.user2)
        response = self.client.get(f'/interviews/room/{self.interview.id}/')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_assessment_access(self):
        self.client.force_login(self.user2)
        response = self.client.get(f'/assessments/analysis/{self.test_obj.id}/')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_roadmap_access(self):
        self.client.force_login(self.user2)
        response = self.client.get(f'/roadmaps/roadmap/?id={self.roadmap.id}')
        # Roadmap view defaults to user's first roadmap if ID is invalid or unauthorized
        self.assertEqual(response.status_code, 200)
        # Verify that the loaded roadmap is NOT user1's roadmap
        self.assertNotIn('Cybersecurity Analyst', response.content.decode())

    def test_invalid_file_upload(self):
        self.client.force_login(self.user1)
        fake_file = SimpleUploadedFile("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", content_type="application/x-msdownload")
        response = self.client.post('/resume/upload/', {
            'resume_file': fake_file,
            'target_role': 'Dev'
        })
        self.assertRedirects(response, '/resume/')
        # Validation should block non-pdf/docx extension

    def test_magic_number_validation(self):
        self.client.force_login(self.user1)
        fake_file = SimpleUploadedFile("malicious.pdf", b"MZ\x90\x00\x03\x00\x00\x00", content_type="application/pdf")
        response = self.client.post('/resume/upload/', {
            'resume_file': fake_file,
            'target_role': 'Dev'
        }, follow=True)
        self.assertContains(response, "Invalid file content")

    def test_ai_endpoint_rate_limiting(self):
        self.client.force_login(self.user1)
        # Assuming we just added the rate limit check
        for _ in range(10):
            Test.objects.create(user=self.user1, skill="Python", completed=True)
            
        response = self.client.post('/assessments/start/', {
            'skill': 'Python',
            'difficulty': 'beginner',
            'num_questions': 5
        }, follow=True)
        self.assertContains(response, "Daily limit reached")
