from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

from .models import Roadmap, PhaseTraining
from assessments.models import Test, TestAnswer
from skills.models import Skill, SkillEvidence

User = get_user_model()

class RoadmapIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='demo', email='demo@test.com', password='password123')
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='password123')
        
        self.roadmap_data = [
            {"phase": "Learn Python", "skills": ["Python"]}
        ]
        
        self.roadmap = Roadmap.objects.create(
            user=self.user,
            target_career="Software Engineer",
            roadmap_data=self.roadmap_data,
            completed_phases=[],
            progress=0
        )
        
        self.test = Test.objects.create(
            user=self.user,
            skill="Learn Python",
            difficulty="beginner",
            num_questions=1,
            completed=False
        )
        
        self.answer = TestAnswer.objects.create(
            test=self.test,
            question="What is Python?",
            options=["A", "B"],
            correct_answer=0,
            topic="Python"
        )
        
        self.pt = PhaseTraining.objects.create(
            roadmap=self.roadmap,
            phase_index=0,
            phase_name="Learn Python",
            test=self.test,
            attempt=1
        )

    def test_update_phase_status_creates_evidence(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('roadmaps:update_phase', kwargs={'roadmap_id': self.roadmap.id}),
            json.dumps({'phase_index': 0, 'completed': True}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.roadmap.refresh_from_db()
        self.assertIn(0, self.roadmap.completed_phases)
        
        # Verify manual checkoff created weak evidence
        evidences = SkillEvidence.objects.filter(user=self.user, skill__name='Python')
        self.assertEqual(evidences.count(), 1)
        self.assertEqual(evidences.first().score, 30)
        
    def test_idor_protection_update_phase_status(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('roadmaps:update_phase', kwargs={'roadmap_id': self.roadmap.id}),
            json.dumps({'phase_index': 0, 'completed': True}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_submit_phase_training_creates_evidence(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('roadmaps:submit_phase_training', kwargs={'pt_id': self.pt.id}),
            json.dumps({'answers': {str(self.answer.id): '0'}, 'time_taken': 30}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.roadmap.refresh_from_db()
        self.assertIn(0, self.roadmap.completed_phases)
        
        # Verify test checkoff created strong evidence
        evidences = SkillEvidence.objects.filter(user=self.user, skill__name='Python')
        self.assertEqual(evidences.count(), 1)
        self.assertEqual(evidences.first().score, 100)
        
    def test_idor_protection_submit_phase_training(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('roadmaps:submit_phase_training', kwargs={'pt_id': self.pt.id}),
            json.dumps({'answers': {str(self.answer.id): '0'}, 'time_taken': 30}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
