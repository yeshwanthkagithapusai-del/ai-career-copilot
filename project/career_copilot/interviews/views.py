"""
Views for interviews app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import InterviewSession, InterviewAnswer, SuggestedQuestion
from ai_services.interview_ai import InterviewAIService
from career_progress.models import CareerProgress


@login_required
def interview_setup(request):
    """Interview setup page."""
    interviews = InterviewSession.objects.filter(user=request.user, completed=True).order_by('-created_at')[:5]
    suggested_questions = SuggestedQuestion.objects.filter(user=request.user)[:10]
    return render(request, 'interviews/interview_setup.html', {
        'interviews': interviews,
        'suggested_questions': suggested_questions,
    })


@login_required
def start_interview(request):
    """Create a new interview session and generate questions."""
    if request.method != 'POST':
        return redirect('interviews:interview_setup')
    
    target_role = request.POST.get('target_role', '').strip()
    interview_type = request.POST.get('interview_type', 'technical')
    difficulty = request.POST.get('difficulty', 'intermediate')
    num_questions = int(request.POST.get('num_questions', 5))
    
    if not target_role:
        messages.error(request, "Please enter a target role.")
        return redirect('interviews:interview_setup')
        
    # Check rate limit (e.g. max 5 interviews per day)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now() - timedelta(days=1)
    if InterviewSession.objects.filter(user=request.user, created_at__gte=today).count() >= 5:
        messages.error(request, "Daily limit reached. You can only start 5 mock interviews per day.")
        return redirect('interviews:interview_setup')
    
    # Get user skills for personalization
    # Get user skills for personalization
    from skills.models import UserSkillProficiency
    user_skills = list(UserSkillProficiency.objects.filter(user=request.user).values_list('skill__name', flat=True))
    
    # Career Context for Intelligence 2.0
    from careers.models import UserCareerGoal
    from career_intelligence.gap_analysis import calculate_skill_gaps
    career_context = ""
    goal = UserCareerGoal.objects.filter(user=request.user).select_related('target_role').first()
    if goal and goal.target_role:
        target_role = goal.target_role.name # Override target role with canonical one if available
        gaps_data = calculate_skill_gaps(request.user, goal.target_role)
        if gaps_data['status'] == 'SUCCESS':
            missing = [g['skill_name'] for g in gaps_data['gaps']['MISSING'][:5]]
            if missing:
                career_context = f"The user needs to improve or demonstrate these missing skills: {', '.join(missing)}."

    # Fetch recent questions served to this user to avoid repeats
    recent_qs = list(
        InterviewAnswer.objects.filter(
            interview__user=request.user
        ).order_by('-created_at').values_list('question', flat=True)[:25]
    )

    # Generate questions
    service = InterviewAIService()
    questions = service.generate_questions(target_role, interview_type, difficulty, num_questions, user_skills, recent_questions=recent_qs, career_context=career_context)
    
    if not questions:
        messages.error(request, "We couldn't generate interview questions. Please try again.")
        return redirect('interviews:interview_setup')
    
    # Create interview session
    interview = InterviewSession.objects.create(
        user=request.user,
        target_role=target_role,
        interview_type=interview_type,
        difficulty=difficulty,
        num_questions=num_questions,
    )
    
    # Store questions and identify primary skill
    from .services import InterviewIntelligenceService
    intel_service = InterviewIntelligenceService()
    
    for q in questions:
        # Determine the primary skill assessed by this question
        assessed_skill = ""
        if interview_type in ['technical', 'mixed']:
            try:
                assessed_skill = intel_service.identify_question_skill(q, target_role, goal)
            except Exception:
                pass

        InterviewAnswer.objects.create(
            interview=interview,
            question=q,
            assessed_skill=assessed_skill
        )
    
    return redirect('interviews:interview_room', interview_id=interview.id)


@login_required
def interview_room(request, interview_id):
    """Interview room - display questions one at a time."""
    interview = get_object_or_404(InterviewSession, id=interview_id, user=request.user)
    answers = interview.answers.all().order_by('id')
    
    return render(request, 'interviews/interview_room.html', {
        'interview': interview,
        'answers': answers,
    })


@login_required
def submit_answer(request, interview_id, answer_id):
    """Submit an answer to an interview question."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    interview = get_object_or_404(InterviewSession, id=interview_id, user=request.user)
    answer = get_object_or_404(InterviewAnswer, id=answer_id, interview=interview)
    
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()
    except Exception:
        user_answer = request.POST.get('answer', '').strip()
    
    if not user_answer:
        return JsonResponse({'error': 'Please provide an answer.'}, status=400)
    
    # Evaluate answer
    service = InterviewAIService()
    evaluation = service.evaluate_answer(
        answer.question, user_answer, interview.target_role,
        interview.interview_type, interview.difficulty
    )
    
    answer.user_answer = user_answer
    answer.ai_feedback = evaluation.get('feedback', '')
    answer.score = evaluation.get('score', 0)
    answer.technical_score = evaluation.get('technical_score', 0)
    answer.communication_score = evaluation.get('communication_score', 0)
    answer.confidence_score = evaluation.get('confidence_score', 0)
    answer.strengths = evaluation.get('strengths', [])
    answer.weaknesses = evaluation.get('weaknesses', [])
    answer.save()

    # Suggestion Box: Save low-scoring questions (score < 70) for later practice
    if answer.score < 70:
        SuggestedQuestion.objects.update_or_create(
            user=request.user,
            question=answer.question,
            defaults={
                'interview': interview,
                'topic': interview.target_role,
                'user_answer': user_answer,
                'score': answer.score,
                'ai_feedback': answer.ai_feedback,
            }
        )
    
    return JsonResponse({
        'success': True,
        'evaluation': evaluation,
    })


@login_required
def complete_interview(request, interview_id):
    """Complete the interview and generate report."""
    interview = get_object_or_404(InterviewSession, id=interview_id, user=request.user)
    
    if interview.completed:
        return redirect('interviews:interview_report', interview_id=interview.id)
    
    answers = interview.answers.all()
    
    # Check all answers are submitted
    unanswered = answers.filter(user_answer='').count()
    if unanswered > 0:
        messages.error(request, f"You have {unanswered} unanswered questions. Please answer all questions before completing the interview.")
        return redirect('interviews:interview_room', interview_id=interview.id)
    
    # Generate report
    service = InterviewAIService()
    answers_data = []
    for answer in answers:
        answers_data.append({
            'question': answer.question,
            'user_answer': answer.user_answer,
            'evaluation': {
                'score': answer.score,
                'technical_score': answer.technical_score,
                'communication_score': answer.communication_score,
                'confidence_score': answer.confidence_score,
                'relevance_score': 0,
                'structure_score': 0,
                'clarity_score': 0,
                'feedback': answer.ai_feedback,
                'strengths': answer.strengths,
                'weaknesses': answer.weaknesses,
            }
        })
        # Save to Suggestion Box if low-scoring
        if answer.score < 70:
            SuggestedQuestion.objects.update_or_create(
                user=request.user,
                question=answer.question,
                defaults={
                    'interview': interview,
                    'topic': interview.target_role,
                    'user_answer': answer.user_answer,
                    'score': answer.score,
                    'ai_feedback': answer.ai_feedback,
                }
            )
    
    report = service.generate_interview_report(answers_data)
    
    if report:
        # Get previous interview for comparison
        previous_interviews = InterviewSession.objects.filter(
            user=request.user, completed=True
        ).exclude(id=interview.id).order_by('-created_at')
        previous_score = previous_interviews.first().overall_score if previous_interviews.exists() else 0
        
        interview.overall_score = report['overall_score']
        interview.technical_score = report['technical_score']
        interview.communication_score = report['communication_score']
        interview.confidence_score = report['confidence_score']
        interview.relevance_score = report['relevance_score']
        interview.structure_score = report['structure_score']
        interview.clarity_score = report['clarity_score']
        interview.strengths = report['strengths']
        interview.weaknesses = report['weaknesses']
        interview.ai_feedback = f"Completed {report['total_questions']} questions. Overall score: {report['overall_score']}/100."
        interview.completed = True
        interview.save()
        
        # Record career progress
        CareerProgress.objects.create(
            user=request.user,
            metric_type='interview_score',
            score=report['overall_score'],
            previous_score=previous_score,
        )
        CareerProgress.objects.create(
            user=request.user,
            metric_type='technical_score',
            score=report['technical_score'],
            previous_score=previous_interviews.first().technical_score if previous_interviews.exists() else 0,
        )
        CareerProgress.objects.create(
            user=request.user,
            metric_type='communication_score',
            score=report['communication_score'],
            previous_score=previous_interviews.first().communication_score if previous_interviews.exists() else 0,
        )
        
        # Record canonical skill evidence from interview via InterviewIntelligenceService
        try:
            from .services import InterviewIntelligenceService
            intel_service = InterviewIntelligenceService()
            intel_service.process_interview_evidence(request.user, interview, answers)
        except Exception as e:
            import logging
            logging.getLogger('interviews').warning(f"Skill evidence extraction failed: {e}")
    
    messages.success(request, f"Interview completed! Your overall score is {report['overall_score']}/100.")
    return redirect('interviews:interview_report', interview_id=interview.id)


@login_required
def interview_report(request, interview_id):
    """Display interview analysis report."""
    interview = get_object_or_404(InterviewSession, id=interview_id, user=request.user, completed=True)
    answers = interview.answers.all()
    suggested_questions = SuggestedQuestion.objects.filter(user=request.user)[:10]
    
    # Get previous interview for comparison
    previous_interviews = InterviewSession.objects.filter(
        user=request.user, completed=True
    ).exclude(id=interview.id).order_by('-created_at')
    previous_interview = previous_interviews.first()
    
    diffs = None
    if previous_interview:
        diffs = {
            'overall': interview.overall_score - previous_interview.overall_score,
            'technical': interview.technical_score - previous_interview.technical_score,
            'communication': interview.communication_score - previous_interview.communication_score,
            'confidence': interview.confidence_score - previous_interview.confidence_score,
        }
    
    # Interview Intelligence 2.0
    from .services import InterviewIntelligenceService
    from careers.models import UserCareerGoal
    from career_intelligence.gap_analysis import calculate_skill_gaps
    
    intel_service = InterviewIntelligenceService()
    goal = UserCareerGoal.objects.filter(user=request.user).select_related('target_role').first()
    gaps_data = calculate_skill_gaps(request.user, goal.target_role) if goal and goal.target_role else None
    
    next_practice = intel_service.generate_next_practice_recommendation(interview, gaps_data)
    
    # Analyze assessed skills and their performances
    skills_demonstrated = []
    skills_needing_improvement = []
    for ans in answers:
        if getattr(ans, 'assessed_skill', '') and ans.assessed_skill.lower() != 'none':
            if ans.technical_score >= 70:
                if ans.assessed_skill not in skills_demonstrated:
                    skills_demonstrated.append(ans.assessed_skill)
            elif ans.technical_score < 70:
                if ans.assessed_skill not in skills_needing_improvement:
                    skills_needing_improvement.append(ans.assessed_skill)
    
    # Calculate target role skills not demonstrated
    not_demonstrated = []
    if gaps_data and gaps_data['status'] == 'SUCCESS':
        all_required = [g['skill_name'] for category in gaps_data['gaps'].values() for g in category]
        not_demonstrated = [s for s in all_required if s not in skills_demonstrated and s not in skills_needing_improvement][:5]
        
    return render(request, 'interviews/interview_report.html', {
        'interview': interview,
        'answers': answers,
        'previous_interview': previous_interview,
        'diffs': diffs,
        'suggested_questions': suggested_questions,
        'next_practice': next_practice,
        'skills_demonstrated': skills_demonstrated,
        'skills_needing_improvement': skills_needing_improvement,
        'not_demonstrated': not_demonstrated,
        'has_goal': bool(goal),
    })


@login_required
def interview_history(request):
    """Display interview history and Suggestion Box."""
    interviews = InterviewSession.objects.filter(user=request.user, completed=True).order_by('-created_at')
    suggested_questions = SuggestedQuestion.objects.filter(user=request.user)[:10]
    return render(request, 'interviews/interview_history.html', {
        'interviews': interviews,
        'suggested_questions': suggested_questions,
    })

