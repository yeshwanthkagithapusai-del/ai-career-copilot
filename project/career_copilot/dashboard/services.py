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
        next_action = DashboardService._determine_next_action(user, target_role, skill_gaps, latest_test)

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
        
    @staticmethod
    def _determine_next_action(user, target_role, skill_gaps, latest_test):
        if not target_role:
            return {
                'title': 'Set your target career',
                'reason': 'To unlock personalized career intelligence, you need to define your goal.',
                'url_name': 'roadmaps:course_guidance'
            }
            
        # Prioritize MISSING critical skills
        missing = skill_gaps.get('MISSING', [])
        critical_missing = [req for req in missing if req['priority'] == 'critical']
        if critical_missing:
            skill = critical_missing[0]['skill_name']
            return {
                'title': f'Learn {skill}',
                'reason': f'{skill} is a critical requirement for your target role.',
                'url_name': 'roadmaps:roadmap'
            }
            
        # Then NEEDS_IMPROVEMENT critical skills
        needs_improvement = skill_gaps.get('NEEDS_IMPROVEMENT', [])
        critical_needs_imp = [item for item in needs_improvement if item['priority'] == 'critical']
        if critical_needs_imp:
            skill = critical_needs_imp[0]['skill_name']
            return {
                'title': f'Improve {skill}',
                'reason': f'Your proficiency in {skill} is below the critical requirement for your role.',
                'url_name': 'roadmaps:roadmap'
            }
            
        # Suggest assessing a DEVELOPING skill
        developing = skill_gaps.get('DEVELOPING', [])
        if developing:
            skill = developing[0]['skill_name']
            return {
                'title': f'Assess {skill}',
                'reason': f'Validate your developing skills by taking a technical assessment.',
                'url_name': 'assessments:test_setup'
            }
            
        # If no gaps or no evidence at all
        if not any([skill_gaps.get('STRONG'), skill_gaps.get('DEVELOPING'), skill_gaps.get('NEEDS_IMPROVEMENT'), skill_gaps.get('MISSING')]):
            return {
                'title': 'Upload your resume',
                'reason': 'Start building your career intelligence profile by uploading a resume.',
                'url_name': 'resume_analyzer:resume_analyzer'
            }
            
        return {
            'title': 'Practice Interviewing',
            'reason': 'Your skills look strong. Start practicing your interview technique.',
            'url_name': 'interviews:interview_setup'
        }
