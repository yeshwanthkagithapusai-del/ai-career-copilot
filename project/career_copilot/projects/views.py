from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProjectTemplate, UserProject
from .services import ProjectService
from careers.models import UserCareerGoal
from career_intelligence.gap_analysis import calculate_skill_gaps

@login_required
def project_list(request):
    """Shows recommended and available projects based on the user's career goal."""
    goal = UserCareerGoal.objects.filter(user=request.user).first()
    target_role = goal.target_role if goal else None
    
    recommended_projects = []
    other_projects = []
    active_projects = UserProject.objects.filter(user=request.user, status='in_progress').select_related('project_template')
    completed_projects = UserProject.objects.filter(user=request.user, status='completed').select_related('project_template')
    
    if target_role:
        gap_data = calculate_skill_gaps(request.user, target_role)
        gaps = gap_data.get('gaps', {}) if gap_data.get('status') == 'SUCCESS' else {}
        recommendations = ProjectService.get_recommended_projects(request.user, target_role, gaps)
        
        # Split into highly recommended vs normal
        for r in recommendations:
            if r['relevance'] == 'high':
                recommended_projects.append(r)
            else:
                other_projects.append(r['project'])
                
        # Also grab any templates not in target role but maybe useful
        role_project_ids = [r['project'].id for r in recommendations]
        all_other = ProjectTemplate.objects.exclude(id__in=role_project_ids)
        other_projects.extend(list(all_other))
    else:
        other_projects = ProjectTemplate.objects.all()

    context = {
        'recommended_projects': recommended_projects,
        'other_projects': other_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'target_role': target_role
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(ProjectTemplate, id=project_id)
    user_project = UserProject.objects.filter(user=request.user, project_template=project).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            ProjectService.start_project(request.user, project.id)
            messages.success(request, f"Started project: {project.title}")
            return redirect('projects:project_detail', project_id=project.id)
        elif action == 'complete':
            if user_project and user_project.status == 'in_progress':
                ProjectService.complete_project(request.user, user_project.id)
                messages.success(request, f"Completed project: {project.title}. Skill evidence recorded!")
                return redirect('projects:project_detail', project_id=project.id)

    context = {
        'project': project,
        'user_project': user_project,
        'skills_developed': project.skills_developed.all()
    }
    return render(request, 'projects/project_detail.html', context)
