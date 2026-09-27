import json
from unittest.mock import patch, MagicMock, PropertyMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import InterviewSession, InterviewAnswer
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal
from skills.models import Skill, SkillEvidence, UserSkillProficiency
from .services import InterviewIntelligenceService

User = get_user_model()

class InterviewIntelligenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', email='test@test.com', password='password123')
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='password123')
        
        self.role = CareerRole.objects.create(name='Data Scientist')
        self.skill_python = Skill.objects.create(name='Python', normalized_name='python')
        CareerRoleSkillRequirement.objects.create(role=self.role, skill=self.skill_python, required_proficiency=80, priority='critical')
        UserCareerGoal.objects.create(user=self.user, target_role=self.role)

    def test_existing_interview_creation_and_room(self):
        self.client.force_login(self.user)
        interview = InterviewSession.objects.create(
            user=self.user, target_role='Data Scientist', interview_type='technical'
        )
        InterviewAnswer.objects.create(interview=interview, question='What is Python?')
        
        response = self.client.get(f'/interviews/room/{interview.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What is Python?')

    def test_idor_protection(self):
        self.client.force_login(self.other_user)
        interview = InterviewSession.objects.create(user=self.user, target_role='Data Scientist')
        response = self.client.get(f'/interviews/room/{interview.id}/')
        self.assertEqual(response.status_code, 404)

    @patch('ai_services.interview_ai.AIService.is_available', new_callable=PropertyMock)
    @patch('ai_services.interview_ai.AIService.chat_completion_json')
    def test_career_goal_influences_generation(self, mock_ai, mock_avail):
        mock_avail.return_value = True
        self.client.force_login(self.user)
        mock_ai.return_value = ["How do you use Python for Data Science?"]
        
        response = self.client.post('/interviews/start/', {
            'target_role': 'Data Scientist',
            'interview_type': 'technical',
            'difficulty': 'intermediate',
            'num_questions': 1
        })
        self.assertEqual(response.status_code, 302)
        
        interview = InterviewSession.objects.filter(user=self.user).first()
        self.assertIsNotNone(interview)
        
        # Verify career context was injected into prompt via mock arguments
        args, kwargs = mock_ai.call_args
        prompt = args[0][1]['content']
        self.assertIn("Python", prompt) # Gap should be included

    @patch('ai_services.openai_service.AIService.is_available', new_callable=PropertyMock)
    @patch('ai_services.openai_service.AIService.chat_completion_json')
    def test_skill_identification_service(self, mock_chat, mock_avail):
        mock_avail.return_value = True
        service = InterviewIntelligenceService()
        mock_chat.return_value = {"skill": "Python"}
        skill = service.identify_question_skill("What is a list comprehension?", "Data Scientist")
        self.assertEqual(skill, "Python")

    def test_performance_creates_skill_evidence(self):
        self.client.force_login(self.user)
        interview = InterviewSession.objects.create(
            user=self.user, target_role='Data Scientist', 
            technical_score=85, communication_score=75
        )
        InterviewAnswer.objects.create(
            interview=interview, question='What is Python?', user_answer='A language',
            technical_score=80, assessed_skill='Python'
        )
        
        service = InterviewIntelligenceService()
        service.process_interview_evidence(self.user, interview, interview.answers.all())
        
        # Domain tech evidence
        ev_tech = SkillEvidence.objects.get(user=self.user, skill__name='Data Scientist')
        self.assertEqual(ev_tech.score, 85)
        
        # Comm evidence
        ev_comm = SkillEvidence.objects.get(user=self.user, skill__name='Communication')
        self.assertEqual(ev_comm.score, 75)
        
        # Specific skill evidence
        ev_py = SkillEvidence.objects.get(user=self.user, skill__name='Python')
        self.assertEqual(ev_py.score, 80)

    @patch('career_intelligence.services.SkillEvidenceService.record_skill_evidence')
    def test_evidence_failure_safe(self, mock_record):
        self.client.force_login(self.user)
        mock_record.side_effect = Exception("DB offline")
        
        interview = InterviewSession.objects.create(
            user=self.user, target_role='Data Scientist', 
            technical_score=85, communication_score=75
        )
        InterviewAnswer.objects.create(
            interview=interview, question='What is Python?', user_answer='A language',
            technical_score=80, assessed_skill='Python'
        )
        
        service = InterviewIntelligenceService()
        # Should not raise exception
        service.process_interview_evidence(self.user, interview, interview.answers.all())
        
    def test_next_practice_recommendation_deterministic(self):
        interview = InterviewSession.objects.create(user=self.user, target_role='Data Scientist')
        # Weak technical score
        InterviewAnswer.objects.create(
            interview=interview, question='What is SQL?', user_answer='idk',
            technical_score=40, assessed_skill='SQL'
        )
        service = InterviewIntelligenceService()
        rec = service.generate_next_practice_recommendation(interview)
        self.assertIn("Practice SQL", rec)
        
    def test_interview_report_shows_intelligence(self):
        self.client.force_login(self.user)
        interview = InterviewSession.objects.create(
            user=self.user, target_role='Data Scientist', completed=True,
            technical_score=85, communication_score=75
        )
        InterviewAnswer.objects.create(
            interview=interview, question='What is Python?', user_answer='A language',
            technical_score=80, assessed_skill='Python', score=80
        )
        
        response = self.client.get(f'/interviews/report/{interview.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Interview Intelligence')
        self.assertContains(response, 'Python')

