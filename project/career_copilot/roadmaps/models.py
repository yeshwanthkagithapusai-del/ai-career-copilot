"""
Models for roadmaps app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Roadmap(models.Model):
    """Stores personalized learning roadmaps."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    target_career = models.CharField(max_length=300)
    current_skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(max_length=100, blank=True, default='beginner')
    study_hours_per_week = models.IntegerField(default=10)
    roadmap_data = models.JSONField(default=list, blank=True)
    progress = models.IntegerField(default=0)
    completed_phases = models.JSONField(default=list, blank=True)
    # Training analytics fields
    training_scores = models.JSONField(default=dict, blank=True)   # {phase_index: latest_score}
    learning_progress = models.IntegerField(default=0)             # avg score across attempted phases
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - Roadmap for {self.target_career}"

    def calculate_progress(self):
        """Calculate overall roadmap completion percentage."""
        if not self.roadmap_data:
            return 0
        total_phases = len(self.roadmap_data)
        completed = len(self.completed_phases) if self.completed_phases else 0
        return int((completed / total_phases) * 100) if total_phases > 0 else 0

    def calculate_learning_progress(self):
        """Calculate average training score across all attempted phases."""
        scores = self.training_scores or {}
        if not scores:
            return 0
        return int(sum(scores.values()) / len(scores))


class Skill(models.Model):
    """Stores user skills and scores."""
    SOURCE_CHOICES = [
        ('resume', 'Resume Analysis'),
        ('test', 'Test Assessment'),
        ('manual', 'Manual Entry'),
        ('roadmap', 'Roadmap'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=200)
    skill_score = models.IntegerField(default=0)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='manual')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-skill_score']
        unique_together = ['user', 'skill_name']

    def __str__(self):
        return f"{self.user.email} - {self.skill_name} ({self.skill_score})"


class PhaseTraining(models.Model):
    """Links a roadmap phase to a training quiz session."""
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='phase_trainings')
    phase_index = models.IntegerField()          # 0-based index of the phase in roadmap_data
    phase_name = models.CharField(max_length=300)
    test = models.ForeignKey(
        'assessments.Test',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='phase_trainings',
    )
    score = models.IntegerField(default=0)       # 0-100
    passed = models.BooleanField(default=False)  # score >= 70 counts as passed
    attempt = models.IntegerField(default=1)     # increments on each retake
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Only the latest attempt per phase matters; unique constraint not set
        # so retakes are allowed (latest record is used).

    def __str__(self):
        status = "Passed" if self.passed else "Failed"
        return (
            f"{self.roadmap.user.email} | {self.roadmap.target_career} | "
            f"Phase {self.phase_index} ({self.phase_name}) | "
            f"Score: {self.score}% | {status} | Attempt #{self.attempt}"
        )
