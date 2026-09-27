from django.test import TestCase
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
