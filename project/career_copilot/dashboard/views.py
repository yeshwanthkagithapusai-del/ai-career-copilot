"""
Views for dashboard app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile, Notification
from resume_analyzer.models import Resume
from interviews.models import InterviewSession
from assessments.models import Test
from roadmaps.models import Roadmap, Skill
from career_progress.models import CareerProgress
from ai_services.career_ai import CareerAIService


@login_required
def dashboard(request):
    """Main dashboard with real user data."""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Fetch real user data
    resumes = Resume.objects.filter(user=user).order_by('-created_at')
    latest_resume = resumes.first()
    previous_resume = resumes[1] if resumes.count() > 1 else None
    
    interviews = InterviewSession.objects.filter(user=user, completed=True).order_by('-created_at')
    latest_interview = interviews.first()
    previous_interview = interviews[1] if interviews.count() > 1 else None
    
    tests = Test.objects.filter(user=user, completed=True).order_by('-created_at')
    latest_test = tests.first()
    previous_test = tests[1] if tests.count() > 1 else None
    
    skills = Skill.objects.filter(user=user).order_by('-skill_score')
    roadmaps = Roadmap.objects.filter(user=user).order_by('-updated_at')
    latest_roadmap = roadmaps.first()
    
    notifications = Notification.objects.filter(user=user)[:5]
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    # Build user context for AI suggestions
    user_data = {
        'ats_scores': [r.ats_score for r in resumes],
        'interview_scores': [{
            'overall': i.overall_score,
            'technical': i.technical_score,
            'communication': i.communication_score,
        } for i in interviews],
        'test_scores': [t.score for t in tests],
        'latest_test': {
            'weak_topics': latest_test.weak_topics if latest_test else [],
        } if latest_test else {},
        'latest_interview': {
            'technical_score': latest_interview.technical_score if latest_interview else 0,
            'communication_score': latest_interview.communication_score if latest_interview else 0,
        } if latest_interview else {},
        'missing_skills': [],
        'roadmap_progress': latest_roadmap.progress if latest_roadmap else 0,
        'has_roadmap': latest_roadmap is not None,
    }
    
    # Get missing skills from latest resume analysis
    if latest_resume and latest_resume.analysis_data:
        user_data['missing_skills'] = latest_resume.analysis_data.get('missing_skills', [])
    
    # Generate AI suggestions
    career_service = CareerAIService()
    ai_suggestions = career_service.generate_suggestions(user_data)
    
    # Calculate score differences
    resume_diff = None
    if latest_resume and previous_resume:
        resume_diff = latest_resume.ats_score - previous_resume.ats_score
    
    interview_diff = None
    if latest_interview and previous_interview:
        interview_diff = {
            'overall': latest_interview.overall_score - previous_interview.overall_score,
            'technical': latest_interview.technical_score - previous_interview.technical_score,
            'communication': latest_interview.communication_score - previous_interview.communication_score,
        }
    
    test_diff = None
    if latest_test and previous_test:
        test_diff = latest_test.score - previous_test.score
    
    context = {
        'profile': profile,
        'latest_resume': latest_resume,
        'previous_resume': previous_resume,
        'resume_diff': resume_diff,
        'latest_interview': latest_interview,
        'previous_interview': previous_interview,
        'interview_diff': interview_diff,
        'interviews_count': interviews.count(),
        'latest_test': latest_test,
        'previous_test': previous_test,
        'test_diff': test_diff,
        'tests_count': tests.count(),
        'skills': skills[:10],
        'latest_roadmap': latest_roadmap,
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        'ai_suggestions': ai_suggestions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
