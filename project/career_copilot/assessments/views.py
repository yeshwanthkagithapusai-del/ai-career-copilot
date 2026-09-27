"""
Views for assessments app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Test, TestAnswer
from ai_services.test_ai import TestAIService
from career_progress.models import CareerProgress

AVAILABLE_SKILLS = [
    # CSE / IT
    'Python', 'SQL', 'Java', 'JavaScript', 'Data Structures',
    'HTML', 'CSS', 'DBMS', 'Operating Systems', 'Computer Networks',
    'Machine Learning', 'C',
    # Mechanical Engineering
    'Thermodynamics', 'Fluid Mechanics', 'Strength of Materials',
    'Control Systems', 'Engineering Mathematics', 'Digital Electronics',
    # Robotics
    'Robotics',
    # Cybersecurity & Cloud
    'Cybersecurity Fundamentals', 'Cloud Computing',
    # UI/UX
    'UI/UX Fundamentals',
]



@login_required
def test_setup(request):
    """Test setup page."""
    tests = Test.objects.filter(user=request.user, completed=True).order_by('-created_at')[:5]
    return render(request, 'tests/test_setup.html', {
        'tests': tests,
        'skills': AVAILABLE_SKILLS,
    })


@login_required
def start_test(request):
    """Create a new test and generate questions."""
    if request.method != 'POST':
        return redirect('assessments:test_setup')
    
    skill = request.POST.get('skill', 'Python')
    difficulty = request.POST.get('difficulty', 'beginner')
    num_questions = int(request.POST.get('num_questions', 10))
    
    # Check rate limit (e.g. max 10 tests per day)
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now() - timedelta(days=1)
    if Test.objects.filter(user=request.user, created_at__gte=today).count() >= 10:
        messages.error(request, "Daily limit reached. You can only start 10 assessments per day.")
        return redirect('assessments:test_setup')
    
    # Generate questions
    service = TestAIService()
    questions = service.generate_questions(skill, difficulty, num_questions)
    
    if not questions:
        messages.error(request, "We couldn't generate test questions. Please try again.")
        return redirect('assessments:test_setup')
    
    # Create test
    test = Test.objects.create(
        user=request.user,
        skill=skill,
        difficulty=difficulty,
        num_questions=num_questions,
    )
    
    # Store questions
    for q in questions:
        TestAnswer.objects.create(
            test=test,
            question=q['question'],
            options=q['options'],
            correct_answer=q['correct'],
            topic=q.get('topic', 'General'),
        )
    
    return redirect('assessments:test_room', test_id=test.id)


@login_required
def test_room(request, test_id):
    """Test room - display questions."""
    test = get_object_or_404(Test, id=test_id, user=request.user)
    answers = test.answers.all().order_by('id')
    
    return render(request, 'tests/test_room.html', {
        'test': test,
        'answers': answers,
    })


@login_required
def submit_test(request, test_id):
    """Submit test and evaluate."""
    if request.method != 'POST':
        return redirect('assessments:test_room', test_id=test_id)
    
    test = get_object_or_404(Test, id=test_id, user=request.user)
    
    if test.completed:
        return redirect('assessments:test_analysis', test_id=test.id)
    
    try:
        data = json.loads(request.body)
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
    except Exception:
        user_answers = {k.replace('answer_', ''): v for k, v in request.POST.items() if k.startswith('answer_')}
        time_taken = int(request.POST.get('time_taken', 0))
    
    # Update answers with user selections
    answers = test.answers.all()
    questions = []
    for answer in answers:
        selected = user_answers.get(str(answer.id), -1)
        answer.selected_answer = int(selected) if selected != '' else -1
        answer.is_correct = answer.selected_answer == answer.correct_answer
        answer.save()
        
        questions.append({
            'question': answer.question,
            'options': answer.options,
            'correct': answer.correct_answer,
            'topic': answer.topic,
        })
    
    # Evaluate test
    service = TestAIService()
    result = service.evaluate_test(questions, user_answers, time_taken)
    
    # Get previous test for comparison
    previous_tests = Test.objects.filter(
        user=request.user, completed=True
    ).exclude(id=test.id).order_by('-created_at')
    previous_score = previous_tests.first().score if previous_tests.exists() else 0
    
    test.score = result['score']
    test.accuracy = result['accuracy']
    test.correct_count = result['correct']
    test.wrong_count = result['wrong']
    test.time_taken = result['time_taken']
    test.topic_performance = result['topic_performance']
    test.strong_topics = result['strong_topics']
    test.weak_topics = result['weak_topics']
    test.suggestions = result['suggestions']
    test.completed = True
    test.save()
    
    # Record career progress
    CareerProgress.objects.create(
        user=request.user,
        metric_type='test_score',
        score=result['score'],
        previous_score=previous_score,
    )
    
    # Update skills
    from roadmaps.models import Skill
    skill_obj, created = Skill.objects.get_or_create(
        user=request.user,
        skill_name=test.skill,
        defaults={'skill_score': result['score'], 'source': 'test'}
    )
    if not created:
        skill_obj.skill_score = result['score']
        skill_obj.source = 'test'
        skill_obj.save()
    
    return JsonResponse({
        'success': True,
        'redirect_url': f'/assessments/analysis/{test.id}/'
    })


@login_required
def test_analysis(request, test_id):
    """Display test analysis."""
    test = get_object_or_404(Test, id=test_id, user=request.user, completed=True)

    answers = test.answers.all()

    previous_tests = Test.objects.filter(completed=True)
    if request.user.is_authenticated:
        previous_tests = previous_tests.filter(user=request.user)
    previous_tests = previous_tests.exclude(id=test_id).order_by('-created_at')
    previous_test = previous_tests.first()

    diff = None
    if previous_test:
        diff = test.score - previous_test.score

    return render(request, 'tests/test_analysis.html', {
        'test': test,
        'answers': answers,
        'previous_test': previous_test,
        'diff': diff,
    })


@login_required
def test_history(request):
    """Display test history."""
    tests = Test.objects.filter(user=request.user, completed=True).order_by('-created_at')
    return render(request, 'tests/test_history.html', {'tests': tests})
