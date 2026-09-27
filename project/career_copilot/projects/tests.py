from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal
from skills.models import Skill, SkillEvidence, UserSkillProficiency
from projects.models import ProjectTemplate, UserProject
from projects.services import ProjectService
from career_intelligence.recommendations import RecommendationEngine

User = get_user_model()

class ProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.role = CareerRole.objects.create(name="Software Engineer")
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        
        self.skill_python = Skill.objects.create(name="Python", normalized_name="python")
        self.skill_django = Skill.objects.create(name="Django", normalized_name="django")
        
        CareerRoleSkillRequirement.objects.create(role=self.role, skill=self.skill_python, priority='critical', required_proficiency=80)
        CareerRoleSkillRequirement.objects.create(role=self.role, skill=self.skill_django, priority='critical', required_proficiency=80)
        
        # User has no evidence yet, so both are missing critical gaps.
        
        self.project_template = ProjectTemplate.objects.create(
            title="Build a CRM",
            description="A full CRM using Django and Python.",
            difficulty="intermediate"
        )
        self.project_template.target_roles.add(self.role)
        self.project_template.skills_developed.add(self.skill_python, self.skill_django)
        
    def test_project_recommendation_routes_to_project(self):
        # Because the user has critical missing skills (Python, Django) and there is a project targeting them, 
        # RecommendationEngine should recommend starting the project.
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "PRACTICE")
        self.assertIn("Start project: Build a CRM", rec.title)
        self.assertEqual(rec.target_url, "projects:project_list")
        
    def test_start_and_complete_project(self):
        # Start project
        up = ProjectService.start_project(self.user, self.project_template.id)
        self.assertEqual(up.status, "in_progress")
        
        # Check recommendation updates to 'Continue project'
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertIn("Continue project: Build a CRM", rec.title)
        
        # Complete project
        completed_up = ProjectService.complete_project(self.user, up.id)
        self.assertEqual(completed_up.status, "completed")
        self.assertIsNotNone(completed_up.completed_at)
        
        # Verify evidence was generated
        evidences = SkillEvidence.objects.filter(user=self.user, source_type='project')
        self.assertEqual(evidences.count(), 2)
        
        python_ev = evidences.get(skill=self.skill_python)
        self.assertEqual(python_ev.score, 100)
        self.assertEqual(python_ev.confidence, 80)
        
        # Verify proficiency recalculated
        prof = UserSkillProficiency.objects.get(user=self.user, skill=self.skill_python)
        self.assertTrue(prof.proficiency_score > 0)
        
    def test_get_recommended_projects_service(self):
        gaps = {
            'MISSING': [{'skill_name': 'Python', 'priority': 'critical'}]
        }
        recommended = ProjectService.get_recommended_projects(self.user, self.role, gaps)
        self.assertEqual(len(recommended), 1)
        self.assertEqual(recommended[0]['project'].title, "Build a CRM")
        self.assertEqual(recommended[0]['relevance'], "high")

class ProjectViewIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="demo", email="demo@test.com", password="password123")
        self.other_user = User.objects.create_user(username="other", email="other@test.com", password="password123")
        
        self.project_template = ProjectTemplate.objects.create(
            title="AI Chatbot",
            description="Build a chatbot.",
            difficulty="intermediate"
        )
        
    def test_project_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Chatbot")
        
    def test_project_start_view(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:project_detail', kwargs={'project_id': self.project_template.id}),
            {'action': 'start'}
        )
        self.assertRedirects(response, reverse('projects:project_detail', kwargs={'project_id': self.project_template.id}))
        
        # Verify it started
        up = UserProject.objects.get(user=self.user, project_template=self.project_template)
        self.assertEqual(up.status, 'in_progress')
        
    def test_project_complete_view_and_idor(self):
        # User starts it
        up = ProjectService.start_project(self.user, self.project_template.id)
        
        # Other user tries to complete it via view - they shouldn't be able to because the view 
        # fetches UserProject for request.user
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('projects:project_detail', kwargs={'project_id': self.project_template.id}),
            {'action': 'complete'}
        )
        # Should not redirect, but render page with 200 and NOT complete user 1's project
        self.assertEqual(response.status_code, 200)
        
        up.refresh_from_db()
        self.assertEqual(up.status, 'in_progress') # Unchanged
        
        # Now user completes it
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('projects:project_detail', kwargs={'project_id': self.project_template.id}),
            {'action': 'complete'}
        )
        self.assertRedirects(response, reverse('projects:project_detail', kwargs={'project_id': self.project_template.id}))
        
        up.refresh_from_db()
        self.assertEqual(up.status, 'completed')
