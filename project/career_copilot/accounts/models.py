"""
Models for accounts app - custom User and UserProfile.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model using email as the unique identifier."""
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_full_name_custom(self):
        return self.full_name or self.username


class UserProfile(models.Model):
    """Extended profile information for each user."""
    DEGREE_CHOICES = [
        ('btech', 'B.Tech'),
        ('mtech', 'M.Tech'),
        ('bca', 'BCA'),
        ('mca', 'MCA'),
        ('bsc', 'B.Sc'),
        ('msc', 'M.Sc'),
        ('diploma', 'Diploma'),
        ('other', 'Other'),
    ]
    
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('graduated', 'Graduated'),
        ('job_seeker', 'Job Seeker'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    college = models.CharField(max_length=300, blank=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, default='btech')
    branch = models.CharField(max_length=200, blank=True)
    academic_year = models.CharField(max_length=20, choices=YEAR_CHOICES, default='1')
    career_goal = models.CharField(max_length=300, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
    
    @property
    def progress_label(self):
        return f"Your journey toward becoming a {self.career_goal}" if self.career_goal else "Your career journey"


class Notification(models.Model):
    """User notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
