"""
Models for assessments app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Test(models.Model):
    """Stores test/assessment session data."""
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    skill = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_LEVELS, default='beginner')
    num_questions = models.IntegerField(default=10)
    
    score = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)  # in seconds
    
    topic_performance = models.JSONField(default=dict, blank=True)
    strong_topics = models.JSONField(default=list, blank=True)
    weak_topics = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.skill} Test ({self.created_at.strftime('%Y-%m-%d')}) - Score: {self.score}"


class TestAnswer(models.Model):
    """Stores individual question answers in a test."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='answers')
    question = models.TextField()
    options = models.JSONField(default=list, blank=True)
    selected_answer = models.IntegerField(default=-1)
    correct_answer = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    topic = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer: {self.question[:50]}..."
