"""
Models for the Careers domain.
"""
from django.db import models
from django.contrib.auth import get_user_model
from skills.models import Skill

User = get_user_model()


class CareerRole(models.Model):
    """A target professional role (e.g., 'Software Developer')."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CareerRoleSkillRequirement(models.Model):
    """A skill required for a specific career role."""
    PRIORITY_CHOICES = [
        ('critical', 'Critical (Must Have)'),
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low / Nice to Have'),
    ]

    role = models.ForeignKey(CareerRole, on_delete=models.CASCADE, related_name='skill_requirements')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='role_requirements')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['role', 'skill']
        ordering = ['role', 'skill']

    def __str__(self):
        return f"{self.role.name} requires {self.skill.name} ({self.priority})"


class UserCareerGoal(models.Model):
    """A user's target career goal."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='career_goal')
    target_role = models.ForeignKey(CareerRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='users_targeting')
    target_title = models.CharField(max_length=200, blank=True, null=True)
    target_company = models.CharField(max_length=200, blank=True, null=True)
    target_industry = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.target_role:
            return f"{self.user.email} -> {self.target_role.name}"
        return f"{self.user.email} -> {self.target_title or 'Unspecified Goal'}"
