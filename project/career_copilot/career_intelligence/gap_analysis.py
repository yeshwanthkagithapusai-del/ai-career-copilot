"""
Skill Gap Analysis module.
"""
from typing import Dict, Any
from careers.models import CareerRole, CareerRoleSkillRequirement
from skills.models import UserSkillProficiency

def calculate_skill_gaps(user, target_role: CareerRole = None) -> Dict[str, Any]:
    """
    Compare User Skill Proficiency against Target Career Requirements.
    Returns categorized skill gaps.
    """
    if not target_role:
        return {'status': 'INSUFFICIENT_DATA', 'message': 'No target role provided.'}
        
    requirements = CareerRoleSkillRequirement.objects.filter(role=target_role).select_related('skill')
    
    if not requirements.exists():
        return {'status': 'INSUFFICIENT_DATA', 'message': 'Target role has no skill requirements defined.'}
        
    proficiencies = {
        p.skill.id: p 
        for p in UserSkillProficiency.objects.filter(user=user).select_related('skill')
    }
    
    gaps = {
        'STRONG': [],
        'DEVELOPING': [],
        'NEEDS_IMPROVEMENT': [],
        'MISSING': []
    }
    
    for req in requirements:
        skill_id = req.skill.id
        if skill_id not in proficiencies:
            gaps['MISSING'].append({
                'skill_name': req.skill.name,
                'priority': req.priority,
                'current_score': 0
            })
            continue
            
        prof = proficiencies[skill_id]
        score = prof.proficiency_score
        
        info = {
            'skill_name': req.skill.name,
            'priority': req.priority,
            'current_score': score,
            'confidence': prof.confidence
        }
        
        if score >= 80:
            gaps['STRONG'].append(info)
        elif score >= 50:
            gaps['DEVELOPING'].append(info)
        else:
            gaps['NEEDS_IMPROVEMENT'].append(info)
            
    return {
        'status': 'SUCCESS',
        'target_role': target_role.name,
        'gaps': gaps
    }
