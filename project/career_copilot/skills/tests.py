from django.test import TestCase
from django.contrib.auth import get_user_model
from skills.models import Skill, SkillAlias, SkillEvidence, UserSkillProficiency
from career_intelligence.services import SkillEvidenceService
from career_intelligence.gap_analysis import calculate_skill_gaps
from careers.models import CareerRole, CareerRoleSkillRequirement

User = get_user_model()

class SkillDomainTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@test.com', password='password')

    def test_skill_normalization_and_creation(self):
        skill = SkillEvidenceService.resolve_skill(" Python Programming ")
        self.assertEqual(skill.name, "Python Programming")
        self.assertEqual(skill.normalized_name, "python programming")
        
        # Test exact match deduplication
        skill2 = SkillEvidenceService.resolve_skill("python programming")
        self.assertEqual(skill.id, skill2.id)

    def test_skill_alias_resolution(self):
        canonical = Skill.objects.create(name="Python", normalized_name="python")
        SkillAlias.objects.create(canonical_skill=canonical, name="python3")
        
        resolved = SkillEvidenceService.resolve_skill("Python3")
        self.assertEqual(resolved.id, canonical.id)

    def test_record_skill_evidence_creates_proficiency(self):
        evidence = SkillEvidenceService.record_skill_evidence(
            user=self.user,
            skill_name="Django",
            source_type="assessment",
            score=85,
            confidence=80
        )
        self.assertIsNotNone(evidence.id)
        
        prof = UserSkillProficiency.objects.get(user=self.user, skill=evidence.skill)
        self.assertEqual(prof.proficiency_score, 85)
        self.assertEqual(prof.evidence_count, 1)

    def test_duplicate_evidence_updates_score(self):
        # Create initial evidence
        ev1 = SkillEvidenceService.record_skill_evidence(
            user=self.user,
            skill_name="React",
            source_type="test",
            source_reference="test-1",
            score=60
        )
        
        # Try to record better score from same source reference
        ev2 = SkillEvidenceService.record_skill_evidence(
            user=self.user,
            skill_name="React",
            source_type="test",
            source_reference="test-1",
            score=90
        )
        
        self.assertEqual(ev1.id, ev2.id)
        ev2.refresh_from_db()
        self.assertEqual(ev2.score, 90)
        
        prof = UserSkillProficiency.objects.get(user=self.user, skill=ev1.skill)
        self.assertEqual(prof.proficiency_score, 90)

    def test_gap_analysis(self):
        role = CareerRole.objects.create(name="Backend Developer")
        skill1 = Skill.objects.create(name="Python", normalized_name="python")
        skill2 = Skill.objects.create(name="SQL", normalized_name="sql")
        skill3 = Skill.objects.create(name="Docker", normalized_name="docker")
        
        CareerRoleSkillRequirement.objects.create(role=role, skill=skill1, priority="critical")
        CareerRoleSkillRequirement.objects.create(role=role, skill=skill2, priority="high")
        CareerRoleSkillRequirement.objects.create(role=role, skill=skill3, priority="medium")
        
        # User has Python (Strong), SQL (Developing), missing Docker
        SkillEvidenceService.record_skill_evidence(self.user, "Python", "manual", score=90)
        SkillEvidenceService.record_skill_evidence(self.user, "SQL", "manual", score=60)
        
        gaps = calculate_skill_gaps(self.user, role)
        
        self.assertEqual(gaps['status'], 'SUCCESS')
        self.assertEqual(len(gaps['gaps']['STRONG']), 1)
        self.assertEqual(gaps['gaps']['STRONG'][0]['skill_name'], "Python")
        
        self.assertEqual(len(gaps['gaps']['DEVELOPING']), 1)
        self.assertEqual(gaps['gaps']['DEVELOPING'][0]['skill_name'], "SQL")
        
        self.assertEqual(len(gaps['gaps']['MISSING']), 1)
        self.assertEqual(gaps['gaps']['MISSING'][0]['skill_name'], "Docker")

    def test_gap_analysis_insufficient_data(self):
        gaps = calculate_skill_gaps(self.user, None)
        self.assertEqual(gaps['status'], 'INSUFFICIENT_DATA')
