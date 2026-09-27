"""
Models for interviews app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class InterviewSession(models.Model):
    """Stores interview session data."""
    INTERVIEW_TYPES = [
        ('technical', 'Technical'),
        ('hr', 'HR'),
        ('behavioral', 'Behavioral'),
        ('mixed', 'Mixed'),
    ]
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    target_role = models.CharField(max_length=300, blank=True, default='')
    interview_type = models.CharField(max_length=50, choices=INTERVIEW_TYPES, default='technical')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_LEVELS, default='intermediate')
    num_questions = models.IntegerField(default=5)
    
    overall_score = models.IntegerField(default=0)
    technical_score = models.IntegerField(default=0)
    communication_score = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    relevance_score = models.IntegerField(default=0)
    structure_score = models.IntegerField(default=0)
    clarity_score = models.IntegerField(default=0)
    
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    ai_feedback = models.TextField(blank=True, default='')
    
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.interview_type} Interview ({self.created_at.strftime('%Y-%m-%d')})"


class InterviewAnswer(models.Model):
    """Stores individual question-answer pairs in an interview."""
    interview = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='answers')
    question = models.TextField()
    user_answer = models.TextField(blank=True, default='')
    ai_feedback = models.TextField(blank=True, default='')
    score = models.IntegerField(default=0)
    technical_score = models.IntegerField(default=0)
    communication_score = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer to: {self.question[:50]}..."


class SuggestedQuestion(models.Model):
    """Stores weak/low-scoring questions for user practice (Suggestion Box)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggested_questions')
    interview = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='suggested_questions', null=True, blank=True)
    topic = models.CharField(max_length=300)
    question = models.TextField()
    user_answer = models.TextField(blank=True, default='')
    score = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - Suggested Q: {self.question[:50]}"

