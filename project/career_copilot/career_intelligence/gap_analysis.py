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
        required_prof = req.required_proficiency
        
        if skill_id not in proficiencies:
            gaps['MISSING'].append({
                'skill_name': req.skill.name,
                'priority': req.priority,
                'current_score': None,
                'required_proficiency': required_prof,
                'gap': required_prof if required_prof is not None else None
            })
            continue
            
        prof = proficiencies[skill_id]
        score = prof.proficiency_score
        
        # Calculate gap if required_prof is available, else None
        gap = None
        if required_prof is not None:
            gap = max(0, required_prof - score)
        
        info = {
            'skill_name': req.skill.name,
            'priority': req.priority,
            'current_score': score,
            'confidence': prof.confidence,
            'required_proficiency': required_prof,
            'gap': gap
        }
        
        # Determine category based on required_proficiency if available
        # If not available, fallback to the generic 50/80 bounds
        if required_prof is not None:
            if score >= required_prof:
                gaps['STRONG'].append(info)
            elif score >= required_prof * 0.7:
                gaps['DEVELOPING'].append(info)
            else:
                gaps['NEEDS_IMPROVEMENT'].append(info)
        else:
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
