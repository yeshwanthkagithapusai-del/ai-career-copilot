from django.test import TestCase
from django.contrib.auth import get_user_model
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal
from skills.models import Skill

User = get_user_model()

class CareerDomainTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@test.com', password='password')
        self.role = CareerRole.objects.create(name="Data Scientist")
        self.skill = Skill.objects.create(name="Python", normalized_name="python")

    def test_career_role_creation(self):
        self.assertEqual(self.role.name, "Data Scientist")
        
    def test_role_skill_requirement(self):
        req = CareerRoleSkillRequirement.objects.create(
            role=self.role,
            skill=self.skill,
            priority='critical'
        )
        self.assertEqual(req.role, self.role)
        self.assertEqual(req.skill, self.skill)
        self.assertEqual(req.priority, 'critical')

    def test_user_career_goal(self):
        goal = UserCareerGoal.objects.create(
            user=self.user,
            target_role=self.role,
            target_title="Senior Data Scientist",
            target_company="Google"
        )
        
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.target_role.name, "Data Scientist")
        self.assertEqual(goal.target_company, "Google")
