"""
Views for career progress app.
"""
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CareerProgress
from ai_services.career_ai import CareerAIService


def career_progress_view(request):
    """Career progress analytics page with real charts."""
    user = request.user if request.user.is_authenticated else None

    if user is None:
        all_progress = CareerProgress.objects.select_related('user').filter(user__username='demo-user').order_by('recorded_at')
    else:
        all_progress = CareerProgress.objects.select_related('user').filter(user=user).order_by('recorded_at')

    metrics = {}
    for record in all_progress:
        if record.metric_type not in metrics:
            metrics[record.metric_type] = []
        metrics[record.metric_type].append({
            'score': record.score,
            'previous_score': record.previous_score,
            'date': record.recorded_at.strftime('%Y-%m-%d %H:%M'),
            'timestamp': record.recorded_at.isoformat(),
        })

    total_records = all_progress.count()
    metric_counts = {k: len(v) for k, v in metrics.items()}
    ai_summary = None

    if total_records:
        user_data = {
            'ats_scores': [m['score'] for m in metrics.get('ats_score', [])],
            'interview_scores': [{'overall': m['score']} for m in metrics.get('interview_score', [])],
            'test_scores': [m['score'] for m in metrics.get('test_score', [])],
            'roadmap_progress': metrics.get('roadmap_progress', [{}])[-1].get('score', 0) if metrics.get('roadmap_progress') else 0,
        }

        service = CareerAIService()
        ai_summary = service.generate_progress_summary(user_data)

    return render(request, 'progress/career_progress.html', {
        'metrics': metrics,
        'metric_counts': metric_counts,
        'ai_summary': ai_summary,
        'total_records': total_records,
    })


def progress_data(request):
    """AJAX endpoint for filtered progress data."""
    metric_type = request.GET.get('metric', 'overall')
    date_filter = request.GET.get('filter', 'all')
    
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    if date_filter == '7d':
        start_date = now - timedelta(days=7)
    elif date_filter == '30d':
        start_date = now - timedelta(days=30)
    elif date_filter == '3m':
        start_date = now - timedelta(days=90)
    else:
        start_date = None
    
    if request.user.is_authenticated:
        queryset = CareerProgress.objects.filter(user=request.user)
    else:
        queryset = CareerProgress.objects.filter(user__username='demo-user')
    
    if metric_type != 'overall':
        queryset = queryset.filter(metric_type=metric_type)
    
    if start_date:
        queryset = queryset.filter(recorded_at__gte=start_date)
    
    records = queryset.order_by('recorded_at')
    
    data = [{
        'metric_type': r.metric_type,
        'score': r.score,
        'previous_score': r.previous_score,
        'date': r.recorded_at.strftime('%b %d, %Y'),
        'timestamp': r.recorded_at.isoformat(),
    } for r in records]
    
    return JsonResponse({'data': data})
