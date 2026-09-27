"""
Career Context Service for Context-Aware Career Copilot.
Gathers structured, safe, and minimized career data for AI Assistant prompts.
"""
from django.utils import timezone
from careers.models import UserCareerGoal
from career_intelligence.gap_analysis import calculate_skill_gaps
from dashboard.services import DashboardService
from resume_analyzer.models import Resume
from interviews.models import InterviewSession
from assessments.models import Test
from roadmaps.models import Roadmap

class CareerContextService:
    """Service to prepare safe, structured career context for the AI Assistant."""

    @staticmethod
    def build_user_context(user) -> dict:
        """
        Builds a structured dictionary containing all relevant user career data.
        Ensures NO raw database objects or secrets are included.
        """
        context = {
            'target_career': None,
            'readiness_score': 0,
            'top_skill_gaps': [],
            'strong_skills': [],
            'recent_evidence': {},
            'roadmap_status': None,
            'next_best_action': None
        }

        # 1. Career Goal, Requirements, Proficiency, Gaps & Readiness
        goal = UserCareerGoal.objects.filter(user=user).select_related('target_role').first()
        if goal and goal.target_role:
            context['target_career'] = goal.target_role.name
            
            # Use deterministic Career Intelligence services for readiness & gaps
            dash_service = DashboardService()
            dash_data = dash_service.get_dashboard_context(user)
            context['readiness_score'] = dash_data.get('readiness_score', 0)
            
            # Fetch NBA
            next_action = dash_data.get('next_action')
            if next_action:
                context['next_best_action'] = {
                    'action': next_action.get('title'),
                    'reason': next_action.get('reason')
                }
            
            gaps_data = calculate_skill_gaps(user, goal.target_role)
            if gaps_data['status'] == 'SUCCESS':
                # Top 3 gaps
                missing = [g['skill_name'] for g in gaps_data['gaps'].get('MISSING', [])]
                informal = [g['skill_name'] for g in gaps_data['gaps'].get('INFORMAL', [])]
                all_gaps = missing + informal
                context['top_skill_gaps'] = all_gaps[:5]

            # Strong skills (proficiency > 70)
            from skills.models import UserSkillProficiency
            strong = UserSkillProficiency.objects.filter(user=user, proficiency_score__gte=70).order_by('-proficiency_score')[:5]
            context['strong_skills'] = [s.skill.name for s in strong]
        
        # 2. Recent Career Activity & Evidence
        # Resume
        latest_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
        if latest_resume:
            context['recent_evidence']['resume'] = {
                'ats_score': latest_resume.ats_score,
                'date': latest_resume.created_at.strftime('%Y-%m-%d')
            }

        # Assessment
        latest_test = Test.objects.filter(user=user).order_by('-created_at').first()
        if latest_test:
            context['recent_evidence']['assessment'] = {
                'score': latest_test.score,
                'topic': latest_test.topic,
                'date': latest_test.created_at.strftime('%Y-%m-%d')
            }

        # Interview
        latest_interview = InterviewSession.objects.filter(user=user, completed=True).order_by('-created_at').first()
        if latest_interview:
            context['recent_evidence']['interview'] = {
                'score': latest_interview.overall_score,
                'target_role': latest_interview.target_role,
                'date': latest_interview.created_at.strftime('%Y-%m-%d')
            }

        # Roadmap
        roadmap = Roadmap.objects.filter(user=user).first()
        if roadmap:
            context['roadmap_status'] = {
                'target_role': roadmap.target_role,
            }
            
        return context

    @staticmethod
    def format_context_for_prompt(context: dict) -> str:
        """
        Formats the context dictionary into a compact string for the LLM prompt.
        """
        lines = ["--- STRUCTURED CAREER CONTEXT ---"]
        
        if context['target_career']:
            lines.append(f"TARGET CAREER:\n{context['target_career']}")
            lines.append(f"\nREADINESS:\n{context['readiness_score']}%")
        else:
            lines.append("TARGET CAREER:\nNot set by user.")

        if context['top_skill_gaps']:
            lines.append(f"\nTOP SKILL GAPS:\n{', '.join(context['top_skill_gaps'])}")

        if context['strong_skills']:
            lines.append(f"\nSTRONG SKILLS:\n{', '.join(context['strong_skills'])}")

        evidence = context.get('recent_evidence', {})
        if evidence:
            lines.append("\nRECENT EVIDENCE:")
            if 'resume' in evidence:
                lines.append(f"- Resume: ATS {evidence['resume']['ats_score']} ({evidence['resume']['date']})")
            if 'assessment' in evidence:
                lines.append(f"- Assessment: {evidence['assessment']['score']} in {evidence['assessment']['topic']} ({evidence['assessment']['date']})")
            if 'interview' in evidence:
                lines.append(f"- Interview: {evidence['interview']['score']} for {evidence['interview']['target_role']} ({evidence['interview']['date']})")

        roadmap = context.get('roadmap_status')
        if roadmap:
            lines.append(f"\nROADMAP:\nTracking towards {roadmap['target_role']}")

        nba = context.get('next_best_action')
        if nba:
            lines.append(f"\nNEXT BEST ACTION:\n{nba['action']}\nReason: {nba['reason']}")

        lines.append("---------------------------------")
        return "\n".join(lines)
