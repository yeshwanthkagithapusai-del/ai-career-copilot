"""
Models for career progress app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CareerProgress(models.Model):
    """Tracks user performance metrics over time."""
    METRIC_TYPES = [
        ('ats_score', 'Resume ATS Score'),
        ('test_score', 'Test Score'),
        ('interview_score', 'Interview Score'),
        ('technical_score', 'Technical Score'),
        ('communication_score', 'Communication Score'),
        ('skill_score', 'Skill Score'),
        ('roadmap_progress', 'Roadmap Progress'),
        ('overall', 'Overall Progress'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_progress')
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    score = models.IntegerField(default=0)
    previous_score = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['recorded_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.metric_type}: {self.score} ({self.recorded_at.strftime('%Y-%m-%d')})"
    
    @property
    def score_difference(self):
        return self.score - self.previous_score
