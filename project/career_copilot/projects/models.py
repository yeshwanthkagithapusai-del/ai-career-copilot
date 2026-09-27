from django.db import models
from django.contrib.auth import get_user_model
from careers.models import CareerRole
from skills.models import Skill

User = get_user_model()


class ProjectTemplate(models.Model):
    """A reusable, canonical project definition that targets specific skills."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed description of what the project is about.")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Relationships to canonical roles and skills
    target_roles = models.ManyToManyField(
        CareerRole, 
        related_name='recommended_projects',
        help_text="The career roles this project is recommended for."
    )
    skills_developed = models.ManyToManyField(
        Skill, 
        related_name='projects',
        help_text="The canonical skills this project builds and provides evidence for."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"


class UserProject(models.Model):
    """Tracks a user's progress through a ProjectTemplate."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    project_template = models.ForeignKey(ProjectTemplate, on_delete=models.CASCADE, related_name='user_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['user', 'project_template']

    def __str__(self):
        return f"{self.user.email} - {self.project_template.title} ({self.get_status_display()})"
