"""
Views for dashboard app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import UserProfile, Notification
from resume_analyzer.models import Resume
from interviews.models import InterviewSession
from assessments.models import Test
from roadmaps.models import Roadmap
from career_progress.models import CareerProgress
from ai_services.career_ai import CareerAIService

from .services import DashboardService

@login_required
def dashboard(request):
    """Main dashboard with real user data."""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Existing notifications logic
    notifications = Notification.objects.filter(user=user)[:5]
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    # Use DashboardService for Career Intelligence context
    service = DashboardService()
    ci_context = service.get_dashboard_context(user)
    
    context = {
        'profile': profile,
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        **ci_context
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def health_check(request):
    """
    Simple unauthenticated health check endpoint for zero-downtime 
    deployments on platforms like Render or AWS ALBs.
    """
    return JsonResponse({'status': 'ok'})
