from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from .models import Test, TestAnswer
from skills.models import Skill, SkillEvidence, UserSkillProficiency
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal

User = get_user_model()

class AssessmentIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='demo-user', email='demo@example.com', password='demo-password123')
        self.other_user = User.objects.create_user(username='other-user', email='other@example.com', password='password123')
        
        self.skill = Skill.objects.create(name='Python', normalized_name='python')
        
        self.test = Test.objects.create(
            user=self.user,
            skill='Python',
            difficulty='beginner',
            num_questions=1,
            completed=False,
        )
        self.answer = TestAnswer.objects.create(
            test=self.test,
            question='What is Python?',
            options=['A', 'B'],
            correct_answer=0,
            topic='General',
        )

    def test_anonymous_user_redirected(self):
        response = self.client.get(reverse('assessments:test_analysis', kwargs={'test_id': self.test.id}))
        self.assertEqual(response.status_code, 302)

    @patch('ai_services.test_ai.TestAIService.evaluate_test')
    def test_submit_test_creates_skill_evidence(self, mock_evaluate):
        self.client.force_login(self.user)
        
        mock_evaluate.return_value = {
            'score': 100,
            'accuracy': 100,
            'correct': 1,
            'wrong': 0,
            'time_taken': 30,
            'topic_performance': {'General': {'accuracy': 100, 'correct': 1, 'total': 1}},
            'strong_topics': [('General', 100)],
            'weak_topics': [],
            'suggestions': ['Good']
        }
        
        response = self.client.post(
            reverse('assessments:submit_test', kwargs={'test_id': self.test.id}),
            {'answer_' + str(self.answer.id): '0', 'time_taken': '30'},
        )
        
        # In Django views, JSON responses from views usually return 200
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        self.test.refresh_from_db()
        self.assertTrue(self.test.completed)
        self.assertEqual(self.test.score, 100)
        
        # Verify SkillEvidence was generated
        evidences = SkillEvidence.objects.filter(user=self.user, skill__name='Python')
        self.assertEqual(evidences.count(), 1)
        self.assertEqual(evidences.first().score, 100)

    def test_idor_protection_on_submit_test(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('assessments:submit_test', kwargs={'test_id': self.test.id}),
            {'answer_' + str(self.answer.id): '0', 'time_taken': '30'},
        )
        # The view uses get_object_or_404(Test, id=test_id, user=request.user)
        self.assertEqual(response.status_code, 404)
        
    def test_idor_protection_on_test_analysis(self):
        self.test.completed = True
        self.test.save()
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('assessments:test_analysis', kwargs={'test_id': self.test.id}))
        self.assertEqual(response.status_code, 404)

