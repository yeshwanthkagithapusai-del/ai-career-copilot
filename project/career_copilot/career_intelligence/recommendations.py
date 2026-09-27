from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from careers.models import UserCareerGoal
from roadmaps.models import Roadmap
from skills.models import SkillEvidence
from resume_analyzer.models import Resume
from assessments.models import Test
from interviews.models import InterviewSession
from career_intelligence.gap_analysis import calculate_skill_gaps

@dataclass
class Recommendation:
    action_type: str
    title: str
    reason: str
    priority: str
    target_url: str
    skill_name: Optional[str] = None
    source: str = "career_intelligence"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type,
            'title': self.title,
            'reason': self.reason,
            'priority': self.priority,
            'target_url': self.target_url,
            'skill_name': self.skill_name,
            'source': self.source,
        }

class RecommendationEngine:
    @staticmethod
    def get_next_best_action(user) -> Recommendation:
        """
        Determines the single most useful actionable career step for the user.
        Evaluates rules in a strict deterministic priority order.
        """
        # 1. Check Target Career
        goal = UserCareerGoal.objects.filter(user=user).select_related('target_role').first()
        if not goal or not goal.target_role:
            return Recommendation(
                action_type="SETUP",
                title="Set your target career",
                reason="To unlock personalized career intelligence, you need to define your goal.",
                priority="CRITICAL",
                target_url="roadmaps:course_guidance"
            )
            
        target_role = goal.target_role

        # 2. Check if Target Career has requirements
        if not target_role.skill_requirements.exists():
            return Recommendation(
                action_type="SETUP",
                title="Complete career profile",
                reason=f"We need to gather more skill requirements for {target_role.name} to give accurate recommendations.",
                priority="CRITICAL",
                target_url="roadmaps:course_guidance"
            )

        # 3. Check for Skill Gaps
        gaps_data = calculate_skill_gaps(user, target_role)
        skill_gaps = gaps_data.get('gaps', {}) if gaps_data.get('status') == 'SUCCESS' else {}
        
        missing = skill_gaps.get('MISSING', [])
        needs_improvement = skill_gaps.get('NEEDS_IMPROVEMENT', [])
        developing = skill_gaps.get('DEVELOPING', [])
        
        critical_missing = [req for req in missing if req.get('priority') == 'critical']
        critical_needs_imp = [req for req in needs_improvement if req.get('priority') == 'critical']
        
        all_critical_gaps = [req.get('skill_name') for req in (critical_missing + critical_needs_imp)]

        # 4. Check Roadmap for active incomplete phase addressing a critical gap
        roadmap = Roadmap.objects.filter(user=user).first()
        if roadmap and roadmap.roadmap_data:
            completed = roadmap.completed_phases or []
            # Find first incomplete phase
            incomplete_phase = None
            for idx, phase in enumerate(roadmap.roadmap_data):
                if idx not in completed:
                    incomplete_phase = phase
                    break
            
            if incomplete_phase:
                phase_title = incomplete_phase.get('title', 'Next Phase')
                phase_skills = [s.strip().lower() for s in incomplete_phase.get('skills', [])]
                
                # Check if this phase targets a critical gap
                targets_critical = any(gap.lower() in phase_skills for gap in all_critical_gaps)
                if targets_critical:
                    return Recommendation(
                        action_type="LEARN",
                        title=f"Continue learning: {phase_title}",
                        reason=f"This roadmap phase addresses one of your highest-priority career gaps for {target_role.name}.",
                        priority="HIGH",
                        target_url="roadmaps:roadmap"
                    )

        # 5. Missing Critical Gaps
        if critical_missing:
            skill = critical_missing[0].get('skill_name')
            return Recommendation(
                action_type="LEARN",
                title=f"Learn {skill}",
                reason=f"{skill} is a critical requirement for {target_role.name}, and you have no evidence of it.",
                priority="HIGH",
                skill_name=skill,
                target_url="roadmaps:roadmap"
            )

        # 6. Needs Improvement Critical Gaps
        if critical_needs_imp:
            skill = critical_needs_imp[0].get('skill_name')
            return Recommendation(
                action_type="IMPROVE",
                title=f"Improve {skill}",
                reason=f"Your proficiency in {skill} is below the critical requirement for {target_role.name}.",
                priority="HIGH",
                skill_name=skill,
                target_url="roadmaps:roadmap"
            )

        # 7. Developing Skills (Needs more evidence/assessment)
        if developing:
            skill = developing[0].get('skill_name')
            return Recommendation(
                action_type="ASSESS",
                title=f"Assess {skill}",
                reason=f"Validate your developing proficiency in {skill} by taking a technical assessment to build stronger evidence.",
                priority="MEDIUM",
                skill_name=skill,
                target_url="assessments:test_setup"
            )

        # 8. Resume Evidence Check
        latest_resume = Resume.objects.filter(user=user).first()
        if not latest_resume:
            return Recommendation(
                action_type="UPLOAD",
                title="Upload your resume",
                reason=f"Start building your career intelligence profile for {target_role.name} by uploading a resume.",
                priority="MEDIUM",
                target_url="resume_analyzer:resume_analyzer"
            )

        # 9. Default: Strong profile, practice interviewing
        return Recommendation(
            action_type="PRACTICE",
            title="Practice Interviewing",
            reason=f"Your skills look strong for {target_role.name}. Start practicing your interview technique to become job-ready.",
            priority="LOW",
            target_url="interviews:interview_setup"
        )
