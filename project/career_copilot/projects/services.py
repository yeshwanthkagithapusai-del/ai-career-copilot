from django.db import transaction
from django.utils import timezone
from .models import ProjectTemplate, UserProject
from career_intelligence.services import SkillEvidenceService
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def get_recommended_projects(user, target_role, skill_gaps: dict):
        """
        Returns a list of ProjectTemplates that would address the user's skill gaps.
        Prioritizes projects that target 'MISSING' or 'NEEDS_IMPROVEMENT' skills.
        """
        if not target_role:
            return []

        # Gather gap skill names
        critical_missing = [req.get('skill_name') for req in skill_gaps.get('MISSING', []) if req.get('priority') == 'critical']
        critical_needs_imp = [req.get('skill_name') for req in skill_gaps.get('NEEDS_IMPROVEMENT', []) if req.get('priority') == 'critical']
        all_critical_gaps = set(critical_missing + critical_needs_imp)
        
        # Get projects that belong to the target role
        projects = ProjectTemplate.objects.filter(target_roles=target_role).prefetch_related('skills_developed')
        
        # Sort or filter based on gaps
        recommended = []
        for p in projects:
            p_skills = set(s.name for s in p.skills_developed.all())
            overlap = p_skills.intersection(all_critical_gaps)
            if overlap:
                recommended.append({
                    'project': p,
                    'addresses_gaps': list(overlap),
                    'relevance': 'high'
                })
            else:
                recommended.append({
                    'project': p,
                    'addresses_gaps': [],
                    'relevance': 'normal'
                })
                
        # Sort high relevance first
        recommended.sort(key=lambda x: 0 if x['relevance'] == 'high' else 1)
        return recommended

    @staticmethod
    def start_project(user, template_id: int):
        """Starts a project for the user."""
        template = ProjectTemplate.objects.get(id=template_id)
        user_project, created = UserProject.objects.get_or_create(
            user=user,
            project_template=template,
            defaults={'status': 'in_progress'}
        )
        return user_project

    @staticmethod
    @transaction.atomic
    def complete_project(user, user_project_id: int):
        """
        Marks a UserProject as completed.
        Automatically generates SkillEvidence for each canonical skill targeted by the project.
        """
        user_project = UserProject.objects.select_related('project_template').get(id=user_project_id, user=user)
        
        if user_project.status == 'completed':
            return user_project # already completed
            
        user_project.status = 'completed'
        user_project.completed_at = timezone.now()
        user_project.save()
        
        # Record Skill Evidence
        template = user_project.project_template
        for skill in template.skills_developed.all():
            try:
                SkillEvidenceService.record_skill_evidence(
                    user=user,
                    skill_name=skill.name,
                    source_type='project',
                    source_reference=f"project:{user_project.id}",
                    description=f"Completed project: {template.title}",
                    score=100,  # Successful project completion implies strong demonstration
                    confidence=80 # High confidence for project work
                )
            except Exception as e:
                logger.error(f"Failed to record project evidence for {skill.name}: {e}")
                # Re-raise to rollback transaction ensuring atomicity
        # Trigger notification
        try:
            from accounts.services import NotificationService
            from django.urls import reverse
            url = reverse('projects:project_list')
            NotificationService.notify_milestone(
                user=user,
                event_name="Project Completed",
                detail=f"You successfully completed the project '{template.title}' and earned new skill evidence.",
                action_url=url,
                ref_id=f"project_completed_{user_project.id}"
            )
        except Exception as e:
            logger.error(f"Failed to generate project notification: {e}")
            
        return user_project
