"""
Career Readiness Snapshot module.
"""
from typing import Dict, Any

def calculate_career_readiness(user, target_role) -> Dict[str, Any]:
    """
    Calculate an overall career readiness score.
    Returns INSUFFICIENT_DATA if there is not enough evidence to score.
    """
    from skills.models import UserSkillProficiency
    
    if not target_role:
        return {'status': 'INSUFFICIENT_DATA', 'message': 'No target role defined.'}
        
    proficiencies = UserSkillProficiency.objects.filter(user=user)
    
    # We require a minimum amount of data before generating a score.
    # For now, they need at least 3 skills evaluated.
    if proficiencies.count() < 3:
        return {'status': 'INSUFFICIENT_DATA', 'message': 'Not enough skill evidence to assess readiness.'}
        
    # Future: weight this by technical skills, resume score, interview performance, etc.
    # Currently just an average of the proficiency scores as a placeholder structure
    avg_score = sum(p.proficiency_score for p in proficiencies) / proficiencies.count()
    
    return {
        'status': 'SUCCESS',
        'readiness_score': int(avg_score),
        'components': {
            'technical_skills': int(avg_score),
            'resume': None,
            'interview': None,
            'assessments': None,
            'projects': None,
            'learning_progress': None,
        }
    }
