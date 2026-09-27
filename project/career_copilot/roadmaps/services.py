"""
Services for the Roadmap domain.
"""
from typing import List, Dict, Any

class RoadmapService:
    
    @staticmethod
    def determine_learning_priorities(skill_gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert categorized skill gaps into an ordered list of learning priorities.
        
        Priority Rules:
        1. Missing critical skills
        2. Needs-improvement critical skills
        3. Missing non-critical skills (high, medium, low)
        4. Needs-improvement non-critical skills
        5. Developing skills
        """
        if not skill_gaps or skill_gaps.get('status') != 'SUCCESS':
            return []
            
        gaps = skill_gaps.get('gaps', {})
        
        missing = gaps.get('MISSING', [])
        needs_improvement = gaps.get('NEEDS_IMPROVEMENT', [])
        developing = gaps.get('DEVELOPING', [])
        
        priorities = []
        
        # 1. Missing critical skills
        for skill in missing:
            if skill.get('priority') == 'critical':
                priorities.append(skill)
                
        # 2. Needs-improvement critical skills
        for skill in needs_improvement:
            if skill.get('priority') == 'critical':
                priorities.append(skill)
                
        # 3. Missing non-critical skills
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        missing_non_critical = [s for s in missing if s.get('priority') != 'critical']
        missing_non_critical.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 99))
        priorities.extend(missing_non_critical)
        
        # 4. Needs-improvement non-critical skills
        ni_non_critical = [s for s in needs_improvement if s.get('priority') != 'critical']
        ni_non_critical.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 99))
        priorities.extend(ni_non_critical)
        
        # 5. Developing skills
        developing_sorted = sorted(developing, key=lambda x: priority_order.get(x.get('priority', 'low'), 99))
        priorities.extend(developing_sorted)
        
        return priorities
