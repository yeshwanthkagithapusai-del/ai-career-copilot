import json
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from skills.models import SkillEvidence, UserSkillProficiency
from roadmaps.models import Roadmap, PhaseTraining
from assessments.models import Test, TestAnswer
from interviews.models import InterviewSession, InterviewAnswer

User = get_user_model()

class IntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@test.com', password='password123')
        self.client.force_login(self.user)

    @patch('ai_services.resume_ai.ResumeAIService.extract_text')
    @patch('ai_services.resume_ai.ResumeAIService.calculate_ats_score')
    def test_resume_analysis_creates_evidence(self, mock_calc, mock_extract):
        mock_extract.return_value = "Python and Django developer with a lot of experience and very long text to bypass the 50 characters length requirement for the resume parser"
        mock_calc.return_value = {
            'overall_score': 85,
            'skills_found': ['Python', 'Django'],
            'skills_missing': [],
            'format_score': 90,
            'keyword_score': 80
        }
        
        # Valid PDF magic number
        fake_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4\ncontent", content_type="application/pdf")
        
        response = self.client.post('/resume/upload/', {
            'resume_file': fake_file,
            'target_role': 'Developer'
        })
        
        self.assertEqual(response.status_code, 302) # Redirects to report
        
        evidences = SkillEvidence.objects.filter(user=self.user, source_type='resume')
        self.assertEqual(evidences.count(), 2)
        skill_names = [e.skill.name for e in evidences]
        self.assertIn("Python", skill_names)
        self.assertIn("Django", skill_names)
        
        prof = UserSkillProficiency.objects.get(user=self.user, skill__name="Python")
        self.assertEqual(prof.proficiency_score, 50) # The default score we set for resume hits

    @patch('ai_services.test_ai.TestAIService.evaluate_test')
    def test_assessment_completion_creates_evidence(self, mock_eval):
        mock_eval.return_value = {
            'score': 100,
            'accuracy': 100,
            'correct': 1,
            'wrong': 0,
            'time_taken': 10,
            'topic_performance': {'React': {'correct': 1, 'total': 1, 'accuracy': 100}},
            'strong_topics': ['React'],
            'weak_topics': [],
            'suggestions': []
        }
        test = Test.objects.create(
            user=self.user,
            skill="React",
            difficulty="intermediate",
            num_questions=1
        )
        TestAnswer.objects.create(
            test=test,
            question="What is React?",
            options=['Library', 'Framework', 'DB', 'OS'],
            correct_answer=0,
            topic="React"
        )
        
        response = self.client.post(f'/assessments/room/{test.id}/submit/', 
            data=json.dumps({'answers': {str(test.answers.first().id): 0}, 'time_taken': 10}), 
            content_type='application/json')
            
        self.assertEqual(response.status_code, 200)
        
        evidence = SkillEvidence.objects.filter(user=self.user, source_type='assessment', skill__name="React").first()
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.score, 100)
        
        prof = UserSkillProficiency.objects.get(user=self.user, skill__name="React")
        self.assertEqual(prof.proficiency_score, 100)

    @patch('ai_services.interview_ai.InterviewAIService.generate_interview_report')
    def test_interview_completion_creates_evidence(self, mock_report):
        mock_report.return_value = {
            'overall_score': 80,
            'technical_score': 85,
            'communication_score': 75,
            'confidence_score': 80,
            'relevance_score': 80,
            'structure_score': 80,
            'clarity_score': 80,
            'strengths': [],
            'weaknesses': [],
            'total_questions': 1
        }
        
        interview = InterviewSession.objects.create(
            user=self.user,
            target_role="Data Scientist"
        )
        InterviewAnswer.objects.create(
            interview=interview,
            question="What is Pandas?",
            user_answer="A data manipulation library",
            score=80,
            technical_score=85,
            communication_score=75,
            confidence_score=80
        )
        
        response = self.client.post(f'/interviews/room/{interview.id}/complete/')
        
        self.assertEqual(response.status_code, 302)
        
        tech_evidence = SkillEvidence.objects.filter(user=self.user, source_type='interview', skill__name="Data Scientist").first()
        self.assertIsNotNone(tech_evidence)
        self.assertEqual(tech_evidence.score, 85)
        
        comm_evidence = SkillEvidence.objects.filter(user=self.user, source_type='interview', skill__name="Communication").first()
        self.assertIsNotNone(comm_evidence)
        self.assertEqual(comm_evidence.score, 75)

    def test_roadmap_training_creates_evidence(self):
        roadmap = Roadmap.objects.create(user=self.user, target_career="Dev")
        test = Test.objects.create(user=self.user, skill="Docker", num_questions=1)
        TestAnswer.objects.create(
            test=test, question="Q1", options=["A"], correct_answer=0
        )
        pt = PhaseTraining.objects.create(
            roadmap=roadmap,
            phase_index=0,
            phase_name="Docker",
            test=test
        )
        
        response = self.client.post(f'/roadmaps/phase-training/{pt.id}/submit/', 
            data=json.dumps({'answers': {str(test.answers.first().id): 0}, 'time_taken': 10}),
            content_type='application/json')
            
        self.assertEqual(response.status_code, 200)
        
        evidence = SkillEvidence.objects.filter(user=self.user, source_type='roadmap', skill__name="Docker").first()
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.score, 100)

    @patch('ai_services.test_ai.TestAIService.evaluate_test')
    @patch('career_intelligence.services.SkillEvidenceService.record_skill_evidence')
    def test_evidence_failure_does_not_break_workflow(self, mock_record, mock_eval):
        mock_record.side_effect = Exception("DB Connection Lost")
        mock_eval.return_value = {
            'score': 100,
            'accuracy': 100,
            'correct': 1,
            'wrong': 0,
            'time_taken': 10,
            'topic_performance': {'React': {'correct': 1, 'total': 1, 'accuracy': 100}},
            'strong_topics': ['React'],
            'weak_topics': [],
            'suggestions': []
        }
        
        # Test assessment
        test = Test.objects.create(user=self.user, skill="FailureTest", num_questions=1)
        TestAnswer.objects.create(
            test=test, question="Q1", options=["A"], correct_answer=0
        )
        
        response = self.client.post(f'/assessments/room/{test.id}/submit/', 
            data=json.dumps({'answers': {str(test.answers.first().id): 0}, 'time_taken': 10}), 
            content_type='application/json')
            
        # Original workflow still succeeds (returns 200 JSON for completion)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
