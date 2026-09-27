"""
Views for roadmaps app - handles course guidance, skill gaps, roadmaps, and phase training.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Roadmap, Skill, PhaseTraining
from ai_services.roadmap_ai import RoadmapAIService
from career_progress.models import CareerProgress


@login_required
def course_guidance(request):
    """Course guidance page with personalized skill recommendations."""
    user = request.user
    profile = getattr(user, 'profile', None)

    # Get current skills
    skills = Skill.objects.filter(user=user)
    current_skills = list(skills.values_list('skill_name', flat=True))

    # Get test performance data
    from assessments.models import Test
    tests = Test.objects.filter(user=user, completed=True).order_by('-created_at')[:5]
    test_performance = {}
    for test in tests:
        for topic, stats in (test.topic_performance or {}).items():
            if topic not in test_performance or stats['accuracy'] < test_performance[topic]:
                test_performance[topic] = stats['accuracy']

    # Generate guidance
    career_goal = profile.career_goal if profile else ''
    degree = profile.degree if profile else ''
    branch = profile.branch if profile else ''
    academic_year = profile.academic_year if profile else '1'

    service = RoadmapAIService()
    guidance = service.generate_course_guidance(
        career_goal, current_skills, degree, branch, academic_year, test_performance
    )

    return render(request, 'roadmap/course_guidance.html', {
        'guidance': guidance,
        'current_skills': current_skills,
        'career_goal': career_goal,
    })


@login_required
def roadmap_view(request):
    """View existing roadmap or generate a new one."""
    user = request.user
    profile = getattr(user, 'profile', None)

    roadmaps = Roadmap.objects.filter(user=user).order_by('-updated_at')
    
    roadmap_id = request.GET.get('id')
    if roadmap_id:
        latest_roadmap = roadmaps.filter(id=roadmap_id).first() or roadmaps.first()
    else:
        latest_roadmap = roadmaps.first()

    show_new_form = request.GET.get('new') == '1'

    skills = Skill.objects.filter(user=user)
    current_skills = list(skills.values_list('skill_name', flat=True))

    # Build per-phase training data as an ordered list parallel to roadmap_data
    # Index = phase_index, value = latest PhaseTraining or None
    phase_training_list = []
    if latest_roadmap:
        total_phases = len(latest_roadmap.roadmap_data)
        # Build lookup dict first
        pt_map = {}
        for pt in PhaseTraining.objects.filter(roadmap=latest_roadmap).order_by('-created_at'):
            if pt.phase_index not in pt_map:
                pt_map[pt.phase_index] = pt
        # Convert to ordered list
        phase_training_list = [pt_map.get(i) for i in range(total_phases)]

    return render(request, 'roadmap/roadmap.html', {
        'roadmap': latest_roadmap,
        'roadmaps': roadmaps,
        'current_skills': current_skills,
        'career_goal': profile.career_goal if profile else '',
        'phase_training_list': phase_training_list,
        'show_new_form': show_new_form,
    })


@login_required
def generate_roadmap(request):
    """Generate a new personalized roadmap."""
    if request.method != 'POST':
        return redirect('/roadmaps/roadmap/?new=1')

    target_career = request.POST.get('target_career', '').strip()
    experience_level = request.POST.get('experience_level', 'beginner')
    study_hours = int(request.POST.get('study_hours_per_week', 10))

    if not target_career:
        messages.error(request, "Please enter your target career.")
        return redirect('/roadmaps/roadmap/?new=1')
        
    # Check rate limit (e.g. max 5 roadmaps per day)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now() - timedelta(days=1)
    if Roadmap.objects.filter(user=request.user, created_at__gte=today).count() >= 5:
        messages.error(request, "Daily limit reached. You can only generate 5 roadmaps per day.")
        return redirect('/roadmaps/roadmap/?new=1')

    user = request.user
    skills = Skill.objects.filter(user=user)
    current_skills = list(skills.values_list('skill_name', flat=True))

    service = RoadmapAIService()
    roadmap_data = service.generate_roadmap(target_career, current_skills, experience_level, study_hours)

    if not roadmap_data:
        messages.error(request, "We couldn't generate a roadmap. Please try again.")
        return redirect('/roadmaps/roadmap/?new=1')

    roadmap = Roadmap.objects.create(
        user=user,
        target_career=target_career,
        current_skills=current_skills,
        experience_level=experience_level,
        study_hours_per_week=study_hours,
        roadmap_data=roadmap_data,
        completed_phases=[],
        progress=0,
        training_scores={},
        learning_progress=0,
    )

    # Record career progress
    CareerProgress.objects.create(
        user=user,
        metric_type='roadmap_progress',
        score=0,
        previous_score=0,
    )

    messages.success(request, f"Your personalized roadmap for '{target_career}' has been generated!")
    return redirect(f'/roadmaps/roadmap/?id={roadmap.id}')




@login_required
def update_phase_status(request, roadmap_id):
    """Update a phase's completion status via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)

    try:
        data = json.loads(request.body)
        phase_index = data.get('phase_index')
        completed = data.get('completed', False)
    except Exception:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    completed_phases = roadmap.completed_phases or []

    if completed:
        if phase_index not in completed_phases:
            completed_phases.append(phase_index)
    else:
        if phase_index in completed_phases:
            completed_phases.remove(phase_index)

    roadmap.completed_phases = completed_phases
    roadmap.progress = roadmap.calculate_progress()
    roadmap.save()

    # Record career progress
    previous_progress = CareerProgress.objects.filter(
        user=request.user, metric_type='roadmap_progress'
    ).order_by('-recorded_at').first()
    previous_score = previous_progress.score if previous_progress else 0

    CareerProgress.objects.create(
        user=request.user,
        metric_type='roadmap_progress',
        score=roadmap.progress,
        previous_score=previous_score,
    )

    return JsonResponse({
        'success': True,
        'progress': roadmap.progress,
        'completed_phases': roadmap.completed_phases,
    })


@login_required
def skills_view(request):
    """View and manage skills."""
    skills = Skill.objects.filter(user=request.user).order_by('-skill_score')

    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        if skill_name:
            skill, created = Skill.objects.get_or_create(
                user=request.user,
                skill_name=skill_name,
                defaults={'skill_score': 0, 'source': 'manual'}
            )
            if created:
                messages.success(request, f"Skill '{skill_name}' added.")
            else:
                messages.info(request, f"Skill '{skill_name}' already exists.")
        return redirect('roadmaps:skills')

    return render(request, 'roadmap/skills.html', {'skills': skills})


# ---------------------------------------------------------------------------
# Phase Training Views
# ---------------------------------------------------------------------------

@login_required
def start_phase_training(request, roadmap_id, phase_index):
    """Generate a training quiz for a specific roadmap phase."""
    if request.method != 'POST':
        return redirect('roadmaps:roadmap')

    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)

    # Validate phase_index
    if not roadmap.roadmap_data or phase_index >= len(roadmap.roadmap_data):
        messages.error(request, "Invalid phase.")
        return redirect('roadmaps:roadmap')

    phase = roadmap.roadmap_data[phase_index]
    phase_name = phase.get('phase', f'Phase {phase_index + 1}')
    skills = phase.get('skills', [])
    topics = phase.get('topics', [])
    difficulty = phase.get('difficulty', 'Beginner')

    # Determine attempt number
    previous_attempts = PhaseTraining.objects.filter(
        roadmap=roadmap, phase_index=phase_index
    ).count()
    attempt_number = previous_attempts + 1

    # Generate questions
    service = RoadmapAIService()
    questions = service.generate_phase_quiz(phase_name, skills, topics, difficulty, num_questions=10)

    if not questions:
        messages.error(request, "Couldn't generate quiz questions. Please try again.")
        return redirect('roadmaps:roadmap')

    # Create a Test record (reuses existing assessments.Test model)
    from assessments.models import Test, TestAnswer
    test = Test.objects.create(
        user=request.user,
        skill=phase_name,
        difficulty=difficulty.lower(),
        num_questions=len(questions),
    )
    for q in questions:
        TestAnswer.objects.create(
            test=test,
            question=q['question'],
            options=q['options'],
            correct_answer=q['correct'],
            topic=q.get('topic', phase_name),
        )

    # Create PhaseTraining record
    phase_training = PhaseTraining.objects.create(
        roadmap=roadmap,
        phase_index=phase_index,
        phase_name=phase_name,
        test=test,
        attempt=attempt_number,
    )

    return redirect('roadmaps:phase_training_room', pt_id=phase_training.id)


@login_required
def phase_training_room(request, pt_id):
    """Display the phase training quiz."""
    pt = get_object_or_404(PhaseTraining, id=pt_id, roadmap__user=request.user)

    if pt.test is None:
        messages.error(request, "Quiz data not found.")
        return redirect('roadmaps:roadmap')

    answers = pt.test.answers.all().order_by('id')

    return render(request, 'roadmap/phase_training_room.html', {
        'pt': pt,
        'test': pt.test,
        'answers': answers,
        'phase_index': pt.phase_index,
    })


@login_required
def submit_phase_training(request, pt_id):
    """Score phase training quiz answers and update learning progress."""
    if request.method != 'POST':
        return redirect('roadmaps:roadmap')

    pt = get_object_or_404(PhaseTraining, id=pt_id, roadmap__user=request.user)

    if pt.test is None or pt.test.completed:
        return JsonResponse({'success': True, 'redirect_url': f'/roadmaps/phase-training/{pt.id}/result/'})

    try:
        data = json.loads(request.body)
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
    except Exception:
        user_answers = {}
        time_taken = 0

    # Score answers
    answers = pt.test.answers.all()
    correct_count = 0
    topic_stats = {}

    for answer in answers:
        selected = user_answers.get(str(answer.id), -1)
        answer.selected_answer = int(selected) if selected != '' else -1
        answer.is_correct = answer.selected_answer == answer.correct_answer
        if answer.is_correct:
            correct_count += 1
        answer.save()

        topic = answer.topic or 'General'
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if answer.is_correct:
            topic_stats[topic]['correct'] += 1

    total = answers.count() or 1
    score = int((correct_count / total) * 100)
    passed = score >= 70

    # Topic performance
    topic_performance = {
        t: {
            'correct': s['correct'],
            'total': s['total'],
            'accuracy': int((s['correct'] / s['total']) * 100) if s['total'] else 0,
        }
        for t, s in topic_stats.items()
    }
    strong_topics = [t for t, s in topic_performance.items() if s['accuracy'] >= 70]
    weak_topics = [t for t, s in topic_performance.items() if s['accuracy'] < 70]

    # Update test record
    test = pt.test
    test.score = score
    test.accuracy = score
    test.correct_count = correct_count
    test.wrong_count = total - correct_count
    test.time_taken = time_taken
    test.topic_performance = topic_performance
    test.strong_topics = strong_topics
    test.weak_topics = weak_topics
    test.completed = True
    test.save()

    # Update PhaseTraining record
    pt.score = score
    pt.passed = passed
    pt.save()

    # Update Roadmap completed_phases, progress, training_scores, and learning_progress
    roadmap = pt.roadmap
    completed_phases = roadmap.completed_phases or []
    if pt.phase_index not in completed_phases:
        completed_phases.append(pt.phase_index)
    roadmap.completed_phases = completed_phases
    roadmap.progress = roadmap.calculate_progress()

    training_scores = roadmap.training_scores or {}
    training_scores[str(pt.phase_index)] = score
    roadmap.training_scores = training_scores
    roadmap.learning_progress = roadmap.calculate_learning_progress()
    roadmap.save()


    # Update or create Skill score for this phase
    Skill.objects.update_or_create(
        user=request.user,
        skill_name=pt.phase_name,
        defaults={'skill_score': score, 'source': 'roadmap'},
    )

    return JsonResponse({
        'success': True,
        'redirect_url': f'/roadmaps/phase-training/{pt.id}/result/',
    })


@login_required
def phase_training_result(request, pt_id):
    """Show phase training quiz results."""
    pt = get_object_or_404(PhaseTraining, id=pt_id, roadmap__user=request.user)

    answers = []
    topic_performance = {}
    strong_topics = []
    weak_topics = []

    if pt.test:
        answers = pt.test.answers.all()
        topic_performance = pt.test.topic_performance or {}
        strong_topics = pt.test.strong_topics or []
        weak_topics = pt.test.weak_topics or []

    # Determine phase data from roadmap
    roadmap = pt.roadmap
    phase_data = {}
    if roadmap.roadmap_data and pt.phase_index < len(roadmap.roadmap_data):
        phase_data = roadmap.roadmap_data[pt.phase_index]

    return render(request, 'roadmap/phase_training_result.html', {
        'pt': pt,
        'answers': answers,
        'topic_performance': topic_performance,
        'strong_topics': strong_topics,
        'weak_topics': weak_topics,
        'phase_data': phase_data,
        'roadmap': roadmap,
    })
