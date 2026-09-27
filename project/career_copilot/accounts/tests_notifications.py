from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Notification
from accounts.services import NotificationService
from careers.models import CareerRole, UserCareerGoal
from career_intelligence.recommendations import RecommendationEngine

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notifyuser', email='notify@example.com', password='password')
        self.role = CareerRole.objects.create(name="Data Scientist")
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)
        from skills.models import Skill
        from careers.models import CareerRoleSkillRequirement
        skill = Skill.objects.create(name="Python")
        CareerRoleSkillRequirement.objects.create(role=self.role, skill=skill, priority='critical', required_proficiency=80)

    def test_create_notification(self):
        n = NotificationService.create_notification(
            user=self.user,
            type="TEST",
            title="Test Title",
            message="Test Message",
            url="/test/",
            ref_id="test_1"
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(n.title, "Test Title")
        self.assertEqual(n.action_url, "/test/")
        
    def test_duplicate_prevention(self):
        # Create first
        NotificationService.create_notification(
            user=self.user,
            type="TEST",
            title="First",
            message="Msg",
            ref_id="dup_123"
        )
        self.assertEqual(Notification.objects.count(), 1)
        
        # Try second with same ref_id
        n2 = NotificationService.create_notification(
            user=self.user,
            type="TEST",
            title="Second",
            message="Msg 2",
            ref_id="dup_123"
        )
        self.assertIsNone(n2)
        self.assertEqual(Notification.objects.count(), 1)

    def test_notify_milestone_appends_nba(self):
        # Notify milestone should query NBA
        n = NotificationService.notify_milestone(
            user=self.user,
            event_name="Project Completed",
            detail="You finished the project.",
            action_url="/dash/",
            ref_id="milestone_1"
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(n.title, "Project Completed")
        # Ensure the appended NBA text is in the message
        self.assertIn("You finished the project.", n.message)
        self.assertIn("Next Best Action", n.message)
