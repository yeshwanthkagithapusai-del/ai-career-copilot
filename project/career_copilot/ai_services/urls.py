"""
AI services URL routes.
"""
from django.urls import path
from . import career_ai
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json


@login_required
def chat_endpoint(request):
    """AI Career Assistant chat endpoint."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Build user context
        user = request.user
        profile = getattr(user, 'profile', None)
        user_context = {}
        if profile:
            user_context['career_goal'] = profile.career_goal
            user_context['full_name'] = profile.full_name
            user_context['degree'] = profile.degree
            user_context['branch'] = profile.branch
            user_context['academic_year'] = profile.academic_year

        # Add performance context
        from resume_analyzer.models import Resume
        from interviews.models import InterviewSession
        from assessments.models import Test
        from roadmaps.models import Roadmap

        latest_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
        if latest_resume:
            user_context['latest_ats_score'] = latest_resume.ats_score

        latest_interview = InterviewSession.objects.filter(user=user).order_by('-created_at').first()
        if latest_interview:
            user_context['latest_interview_score'] = latest_interview.overall_score

        latest_test = Test.objects.filter(user=user).order_by('-created_at').first()
        if latest_test:
            user_context['latest_test_score'] = latest_test.score

        service = career_ai.CareerAIService()
        response = service.chat(message, user_context)

        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': 'Something went wrong. Please try again.'}, status=500)


@login_required
def transcribe_audio(request):
    """
    Transcribe audio using OpenAI Whisper API.
    Accepts a multipart/form-data POST with an 'audio' file field.
    Falls back gracefully if OpenAI API key is not configured.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided.'}, status=400)

    from django.conf import settings
    api_key = getattr(settings, 'OPENAI_API_KEY', '')

    if not api_key:
        return JsonResponse({
            'success': False,
            'error': 'no_api_key',
            'message': 'OpenAI API key not configured. Please type your answer manually.',
        }, status=200)

    try:
        import tempfile
        import os
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Determine file extension from content type
        suffix = '.webm'
        content_type = audio_file.content_type or ''
        if 'ogg' in content_type:
            suffix = '.ogg'
        elif 'mp4' in content_type or 'mpeg' in content_type:
            suffix = '.mp4'
        elif 'wav' in content_type:
            suffix = '.wav'

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            with open(tmp_path, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=f,
                    response_format='text',
                )
            return JsonResponse({'success': True, 'transcript': transcript.strip()})
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'transcription_failed',
            'message': f'Transcription failed: {str(e)}',
        }, status=200)


app_name = 'ai_services'

urlpatterns = [
    path('chat/', chat_endpoint, name='chat'),
    path('transcribe/', transcribe_audio, name='transcribe_audio'),
]
