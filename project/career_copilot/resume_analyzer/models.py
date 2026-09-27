"""
Models for resume analyzer app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Resume(models.Model):
    """Stores uploaded resumes and their analysis."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    resume_file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, default='')
    ats_score = models.IntegerField(default=0)
    previous_ats_score = models.IntegerField(default=0)
    target_role = models.CharField(max_length=300, blank=True, default='')
    job_description = models.TextField(blank=True, default='')
    analysis_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Resume ({self.created_at.strftime('%Y-%m-%d')}) - ATS: {self.ats_score}"
    
    @property
    def score_difference(self):
        return self.ats_score - self.previous_ats_score
