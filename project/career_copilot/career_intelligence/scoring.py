"""
Scoring and proficiency calculation logic.
"""
from django.db.models import Max, Avg, Count
from skills.models import UserSkillProficiency, SkillEvidence

def recalculate_user_proficiency(user, skill):
    """
    Recalculate the user's proficiency for a given skill based on all evidence.
    This provides a deterministic way to roll up evidence into a single score.
    """
    evidences = SkillEvidence.objects.filter(user=user, skill=skill)
    count = evidences.count()
    if count == 0:
        return None
        
    # Simple deterministic rule:
    # Base score on highest quantitative score provided by evidence
    max_score = evidences.aggregate(Max('score'))['score__max'] or 0
    
    # Calculate confidence based on evidence count
    # 1 piece = 40%, 2 = 60%, 3 = 80%, 4+ = 90%
    confidence = min(90, 40 + (count - 1) * 20) if count > 0 else 0
    
    proficiency, created = UserSkillProficiency.objects.update_or_create(
        user=user,
        skill=skill,
        defaults={
            'proficiency_score': max_score,
            'confidence': confidence,
            'evidence_count': count
        }
    )
    return proficiency
