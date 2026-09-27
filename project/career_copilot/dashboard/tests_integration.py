import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from careers.models import UserCareerGoal, CareerRole, CareerRoleSkillRequirement
from skills.models import Skill, UserSkillProficiency, SkillEvidence
from resume_analyzer.models import Resume

User = get_user_model()

class DashboardIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test@test.com', email='test@test.com', password='password123')
        
    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
        
    def test_dashboard_empty_state_no_career_goal(self):
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set your target career')
        self.assertFalse(response.context.get('has_target_career'))
        
    def test_dashboard_with_career_goal_and_gaps(self):
        # Create a career role
        role = CareerRole.objects.create(name='Backend Developer')
        skill = Skill.objects.create(name='Python', normalized_name='python')
        CareerRoleSkillRequirement.objects.create(
            role=role, skill=skill, priority='critical'
        )
        
        # Set user goal
        UserCareerGoal.objects.create(user=self.user, target_role=role)
        
        # Add some evidence and proficiency
        SkillEvidence.objects.create(
            user=self.user, skill=skill, source_type='resume', score=50, confidence=80
        )
        UserSkillProficiency.objects.create(
            user=self.user, skill=skill, proficiency_score=50, confidence=80
        )
        
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_target_career'])
        
        # The user has 50 proficiency, required is 80 (default without req). Should be in DEVELOPING (>=50)
        gaps = response.context['skill_gaps']
        self.assertTrue(len(gaps['DEVELOPING']) > 0)
        
        # Next action should point to assessing Python (since developing)
        next_action = response.context['next_action']
        self.assertIn('Python', next_action['title'])
        self.assertIn('Assess', next_action['title'])
        
        # Evidence counts should show resume
        evidence_counts = response.context['evidence_counts']
        self.assertEqual(evidence_counts.get('resume'), 1)

    def test_dashboard_chart_data_contract_and_required_proficiency(self):
        # Create a career role
        role = CareerRole.objects.create(name='Frontend Developer')
        skill_react = Skill.objects.create(name='React', normalized_name='react')
        skill_css = Skill.objects.create(name='CSS', normalized_name='css')
        skill_missing = Skill.objects.create(name='Jest', normalized_name='jest')
        
        CareerRoleSkillRequirement.objects.create(
            role=role, skill=skill_react, priority='critical', required_proficiency=90
        )
        CareerRoleSkillRequirement.objects.create(
            role=role, skill=skill_css, priority='medium', required_proficiency=None # Genuinely unavailable
        )
        CareerRoleSkillRequirement.objects.create(
            role=role, skill=skill_missing, priority='high', required_proficiency=75
        )
        
        # Set user goal
        UserCareerGoal.objects.create(user=self.user, target_role=role)
        
        # Add some evidence and proficiency
        UserSkillProficiency.objects.create(
            user=self.user, skill=skill_react, proficiency_score=60, confidence=90
        )
        UserSkillProficiency.objects.create(
            user=self.user, skill=skill_css, proficiency_score=85, confidence=90
        )
        
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check chart data contract
        chart_data = response.context['skill_gaps_json']
        self.assertEqual(len(chart_data), 3)
        
        # Missing skill (Jest)
        jest_data = next(item for item in chart_data if item['skill_name'] == 'Jest')
        self.assertIsNone(jest_data['current_proficiency'])
        self.assertEqual(jest_data['required_proficiency'], 75)
        self.assertEqual(jest_data['priority'], 'high')
        self.assertEqual(jest_data['category'], 'MISSING')
        
        # React skill (Needs Improvement, 60 < 90)
        react_data = next(item for item in chart_data if item['skill_name'] == 'React')
        self.assertEqual(react_data['current_proficiency'], 60)
        self.assertEqual(react_data['required_proficiency'], 90)
        self.assertEqual(react_data['gap'], 30)
        self.assertEqual(react_data['category'], 'NEEDS_IMPROVEMENT') # 60 < 90 * 0.7 = 63
        # Wait, if 60 < 63 it's NEEDS_IMPROVEMENT. Let's not assert the exact category if math is tricky, but we know it's not STRONG.
        
        # CSS skill (Strong, 85, no requirement)
        css_data = next(item for item in chart_data if item['skill_name'] == 'CSS')
        self.assertEqual(css_data['current_proficiency'], 85)
        self.assertIsNone(css_data['required_proficiency'])
        self.assertIsNone(css_data['gap'])
        self.assertEqual(css_data['category'], 'STRONG') # Falls back to 80 threshold

    def test_cross_user_data_leakage(self):
        other_user = User.objects.create_user(username='other@test.com', email='other@test.com', password='password123')
        
        role = CareerRole.objects.create(name='Data Scientist')
        skill = Skill.objects.create(name='Python2', normalized_name='python2')
        CareerRoleSkillRequirement.objects.create(
            role=role, skill=skill, priority='critical', required_proficiency=90
        )
        
        UserCareerGoal.objects.create(user=other_user, target_role=role)
        UserSkillProficiency.objects.create(
            user=other_user, skill=skill, proficiency_score=100, confidence=90
        )
        
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_target_career'])
        # Current user should not see other user's goals or skills
        self.assertEqual(len(response.context['skill_gaps_json']), 0)
