"""
Dashboard Service Layer.
Prepares view models and coordinates Career Intelligence data.
"""
from django.db.models import Count
from careers.models import UserCareerGoal
from skills.models import SkillEvidence
from career_intelligence.readiness import calculate_career_readiness
from career_intelligence.gap_analysis import calculate_skill_gaps
from resume_analyzer.models import Resume
from assessments.models import Test
from interviews.models import InterviewSession
from roadmaps.models import PhaseTraining


class DashboardService:
    @staticmethod
    def get_dashboard_context(user):
        """Prepare the comprehensive view model for the dashboard."""
        
        # 1. Career Target
        goal = UserCareerGoal.objects.filter(user=user).first()
        target_role = goal.target_role if goal else None
        
        # 2. Career Readiness & 3. Skill Gaps
        readiness_score = None
        readiness_data = {}
        skill_gaps = {
            'STRONG': [],
            'DEVELOPING': [],
            'NEEDS_IMPROVEMENT': [],
            'MISSING': []
        }
        
        if target_role:
            readiness_data = calculate_career_readiness(user, target_role)
            if readiness_data.get('status') == 'SUCCESS':
                readiness_score = readiness_data.get('score')
            
            gaps_data = calculate_skill_gaps(user, target_role)
            if gaps_data.get('status') == 'SUCCESS':
                skill_gaps = gaps_data.get('gaps', skill_gaps)
        
        # 4. Evidence Summary
        # Get count of distinct skills per source type
        evidence_counts = {}
        counts = SkillEvidence.objects.filter(user=user).values('source_type').annotate(count=Count('skill', distinct=True))
        for item in counts:
            evidence_counts[item['source_type']] = item['count']
            
        # 5. Recent Career Activity
        activities = []
        
        latest_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
        if latest_resume:
            activities.append({
                'type': 'Resume Analyzed',
                'date': latest_resume.created_at,
                'detail': f"ATS Score: {latest_resume.ats_score}"
            })
            
        latest_test = Test.objects.filter(user=user, completed=True).order_by('-created_at').first()
        if latest_test:
            activities.append({
                'type': 'Assessment Completed',
                'date': latest_test.created_at,
                'detail': f"{latest_test.skill}: {latest_test.score}%"
            })
            
        latest_interview = InterviewSession.objects.filter(user=user, completed=True).order_by('-created_at').first()
        if latest_interview:
            activities.append({
                'type': 'Interview Completed',
                'date': latest_interview.created_at,
                'detail': f"Target Role: {latest_interview.target_role} ({latest_interview.overall_score}%)"
            })
            
        latest_pt = PhaseTraining.objects.filter(roadmap__user=user, passed=True).order_by('-created_at').first()
        if latest_pt:
            activities.append({
                'type': 'Training Completed',
                'date': latest_pt.created_at,
                'detail': f"Phase: {latest_pt.phase_name}"
            })
            
        # Sort by date descending and take top 5
        activities.sort(key=lambda x: x['date'], reverse=True)
        activities = activities[:5]

        # 6. Next Best Action (Deterministic)
        from career_intelligence.recommendations import RecommendationEngine
        nba = RecommendationEngine.get_next_best_action(user)
        next_action = {
            'title': nba.title,
            'reason': nba.reason,
            'url_name': nba.target_url
        }

        # Prepare chart data
        chart_data = []
        
        # Collect top 10 gaps for the chart
        categories = [
            ('MISSING', skill_gaps.get('MISSING', [])),
            ('NEEDS_IMPROVEMENT', skill_gaps.get('NEEDS_IMPROVEMENT', [])),
            ('DEVELOPING', skill_gaps.get('DEVELOPING', [])),
            ('STRONG', skill_gaps.get('STRONG', []))
        ]
        
        for category, gap_list in categories:
            for gap in gap_list:
                if len(chart_data) >= 10:
                    break
                chart_data.append({
                    'skill_name': gap.get('skill_name'),
                    'current_proficiency': gap.get('current_score'),
                    'required_proficiency': gap.get('required_proficiency'),
                    'gap': gap.get('gap'),
                    'priority': gap.get('priority'),
                    'category': category
                })
            if len(chart_data) >= 10:
                break

        return {
            'has_target_career': target_role is not None,
            'target_role': target_role,
            'readiness_score': readiness_score,
            'skill_gaps': skill_gaps,
            'evidence_counts': evidence_counts,
            'activities': activities,
            'next_action': next_action,
            'skill_gaps_json': chart_data
        }
