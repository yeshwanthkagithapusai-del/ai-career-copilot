"""
Career Intelligence Core Services.
Provides high-level APIs for interacting with the career and skills domain.
"""
from django.db import transaction
from django.utils import timezone
from skills.models import Skill, SkillAlias, SkillEvidence, UserSkillProficiency
from careers.models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal
from .scoring import recalculate_user_proficiency

class SkillEvidenceService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    @staticmethod
    def resolve_skill(skill_name: str) -> Skill:
        """Find or create a canonical skill, checking aliases."""
        normalized = SkillEvidenceService._normalize_name(skill_name)
        
        # 1. Check exact match on Skill
        skill = Skill.objects.filter(normalized_name=normalized).first()
        if skill:
            return skill
            
        # 2. Check Aliases
        alias = SkillAlias.objects.filter(name=normalized).select_related('canonical_skill').first()
        if alias:
            return alias.canonical_skill
            
        # 3. Create new canonical skill if not found
        skill = Skill.objects.create(
            name=skill_name.strip(),
            normalized_name=normalized
        )
        return skill

    @staticmethod
    @transaction.atomic
    def record_skill_evidence(user, skill_name: str, source_type: str, 
                              source_reference: str = None, description: str = "", 
                              score: int = None, confidence: int = 50) -> SkillEvidence:
        """Record evidence for a skill and update user proficiency."""
        
        skill = SkillEvidenceService.resolve_skill(skill_name)
        
        # Check for duplicates (e.g. same test ID)
        if source_reference:
            existing = SkillEvidence.objects.filter(
                user=user, 
                skill=skill, 
                source_type=source_type, 
                source_reference=source_reference
            ).first()
            if existing:
                # Update existing if confidence/score improved or just return
                changed = False
                if score is not None:
                    if existing.score is None or score > existing.score:
                        existing.score = score
                        changed = True
                if confidence > existing.confidence:
                    existing.confidence = confidence
                    changed = True
                
                if changed:
                    existing.evidence_description = description
                    existing.save()
                    recalculate_user_proficiency(user, skill)
                return existing
                
        # Create new evidence
        evidence = SkillEvidence.objects.create(
            user=user,
            skill=skill,
            source_type=source_type,
            source_reference=source_reference,
            evidence_description=description,
            score=score,
            confidence=confidence
        )
        
        recalculate_user_proficiency(user, skill)
        return evidence
