from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
import json

from .models import Roadmap, PhaseTraining, Skill as LegacySkill
from assessments.models import Test, TestAnswer
from skills.models import Skill, SkillEvidence, UserSkillProficiency

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


class SkillsViewTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='skilluser', email='skilluser@test.com', password='password123')

    def test_skills_view_renders_canonical_proficiencies(self):
        self.client.force_login(self.user)
        py_skill = Skill.objects.create(name='Python', normalized_name='python')
        docker_skill = Skill.objects.create(name='Docker', normalized_name='docker')

        UserSkillProficiency.objects.create(
            user=self.user,
            skill=py_skill,
            proficiency_score=85,
            confidence=70,
            evidence_count=2
        )
        UserSkillProficiency.objects.create(
            user=self.user,
            skill=docker_skill,
            proficiency_score=0,
            confidence=40,
            evidence_count=1
        )

        response = self.client.get(reverse('roadmaps:skills'))
        self.assertEqual(response.status_code, 200)

        # Verify skill names render in HTML
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Docker')

        # Verify skill scores render in HTML
        self.assertContains(response, '85')
        self.assertContains(response, '0')
        self.assertContains(response, 'width: 85%;')
        self.assertContains(response, 'width: 0%;')

        # Verify confidence badges
        self.assertContains(response, '70% conf')
        self.assertContains(response, '40% conf')

        # Verify Chart.js data
        self.assertContains(response, '"Python"')
        self.assertContains(response, '"Docker"')

    def test_skills_view_empty_state(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('roadmaps:skills'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No skills tracked yet')
        self.assertContains(response, 'Tracked Skills (0)')

    def test_skills_view_post_creates_canonical_skill_and_renders(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('roadmaps:skills'),
            {'skill_name': 'TypeScript'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TypeScript')
        self.assertTrue(Skill.objects.filter(normalized_name='typescript').exists())
        self.assertTrue(UserSkillProficiency.objects.filter(user=self.user, skill__normalized_name='typescript').exists())

    def test_skills_template_legacy_object_fallback(self):
        legacy = LegacySkill.objects.create(
            user=self.user,
            skill_name='LegacySQL',
            skill_score=65,
            source='manual'
        )
        request = self.factory.get(reverse('roadmaps:skills'))
        request.user = self.user
        html = render_to_string('roadmap/skills.html', {'skills': [legacy]}, request=request)
        self.assertIn('LegacySQL', html)
        self.assertIn('65', html)
        self.assertIn('width: 65%;', html)
        self.assertIn('manual', html)
