from django.test import TestCase
from django.contrib.auth import get_user_model
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal
from roadmaps.models import Roadmap
from resume_analyzer.models import Resume
from skills.models import SkillEvidence, UserSkillProficiency, Skill as AppSkill
from career_intelligence.recommendations import RecommendationEngine

User = get_user_model()

class RecommendationEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.role = CareerRole.objects.create(name="Software Engineer", description="Builds software")
        
        self.skill_python = AppSkill.objects.create(name="Python", normalized_name="python", category="technical")
        self.skill_sql = AppSkill.objects.create(name="SQL", normalized_name="sql", category="technical")
        
        CareerRoleSkillRequirement.objects.create(
            role=self.role,
            skill=self.skill_python,
            priority="critical",
            required_proficiency=80
        )
        CareerRoleSkillRequirement.objects.create(
            role=self.role,
            skill=self.skill_sql,
            priority="critical",
            required_proficiency=70
        )

    def test_no_target_career(self):
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "SETUP")
        self.assertEqual(rec.title, "Set your target career")
        self.assertEqual(rec.target_url, "roadmaps:course_guidance")

    def test_target_career_with_no_requirements(self):
        empty_role = CareerRole.objects.create(name="Empty Role")
        UserCareerGoal.objects.create(user=self.user, target_role=empty_role)
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "SETUP")
        self.assertEqual(rec.title, "Complete career profile")
        self.assertEqual(rec.target_url, "roadmaps:course_guidance")

    def test_critical_missing_skill_gap(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        # User has no evidence for Python or SQL, so both are MISSING critical
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "LEARN")
        self.assertIn("Learn", rec.title)
        self.assertIn(rec.skill_name, ["Python", "SQL"])
        self.assertEqual(rec.target_url, "roadmaps:roadmap")

    def test_active_incomplete_roadmap_phase(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        # Create an incomplete roadmap phase targeting Python
        Roadmap.objects.create(
            user=self.user,
            target_career=self.role.name,
            roadmap_data=[
                {"title": "Learn Python", "skills": ["Python"]}
            ],
            completed_phases=[]
        )
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "LEARN")
        self.assertEqual(rec.title, "Continue learning: Learn Python")
        self.assertEqual(rec.target_url, "roadmaps:roadmap")

    def test_critical_needs_improvement_skill_gap(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        # Provide some evidence for Python, but low proficiency (e.g., 40 vs required 80)
        # And evidence for SQL to avoid missing
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_python, proficiency_score=40)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_sql, proficiency_score=70) # SQL is met

        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "IMPROVE")
        self.assertEqual(rec.title, "Improve Python")
        self.assertEqual(rec.target_url, "roadmaps:roadmap")

    def test_developing_skill(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        # 50 to 69 is usually DEVELOPING depending on strict requirements, but let's say require=80, score=60 -> NEEDS_IMPROVEMENT.
        # Wait, if require=80, score=60, it's NEEDS_IMPROVEMENT if gap is > 10.
        # Let's set require=80, score=75 -> DEVELOPING.
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_python, proficiency_score=75)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_sql, proficiency_score=75) # Met requirement 70

        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "ASSESS")
        self.assertEqual(rec.title, "Assess Python")
        self.assertEqual(rec.target_url, "assessments:test_setup")

    def test_no_resume_evidence(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        # User has met all requirements (score 80 and 70)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_python, proficiency_score=80)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_sql, proficiency_score=70)
        
        # No resume uploaded
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "UPLOAD")
        self.assertEqual(rec.title, "Upload your resume")
        self.assertEqual(rec.target_url, "resume_analyzer:resume_analyzer")

    def test_strong_profile_no_gaps(self):
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_python, proficiency_score=80)
        UserSkillProficiency.objects.create(user=self.user, skill=self.skill_sql, proficiency_score=70)
        Resume.objects.create(user=self.user, ats_score=80)
        
        rec = RecommendationEngine.get_next_best_action(self.user)
        self.assertEqual(rec.action_type, "PRACTICE")
        self.assertEqual(rec.title, "Practice Interviewing")
        self.assertEqual(rec.target_url, "interviews:interview_setup")
