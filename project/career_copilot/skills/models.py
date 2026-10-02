"""
Models for the Skills domain.
This acts as the canonical source of truth for skills, evidence, and proficiency.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Skill(models.Model):
    """Canonical representation of a skill."""
    name = models.CharField(max_length=200)
    normalized_name = models.CharField(max_length=200, unique=True, help_text="Lowercase, whitespace-normalized name for deduplication")
    category = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Programming, Soft Skill, Cloud")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['normalized_name']

    def __str__(self):
        return self.name


class SkillAlias(models.Model):
    """Alternate names for a canonical skill (e.g., 'Python Programming' -> 'Python')."""
    canonical_skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='aliases')
    name = models.CharField(max_length=200, unique=True, help_text="The alias name, usually normalized")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Skill aliases"

    def __str__(self):
        return f"{self.name} -> {self.canonical_skill.name}"


class SkillEvidence(models.Model):
    """Evidence that a user possesses a skill."""
    SOURCE_CHOICES = [
        ('resume', 'Resume Analysis'),
        ('assessment', 'Test Assessment'),
        ('interview', 'AI Interview'),
        ('roadmap', 'Roadmap Training'),
        ('project', 'Project Experience'),
        ('manual', 'Manual Entry'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_evidences')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='evidences')
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_reference = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'resume:5' or 'test:12'")
    evidence_description = models.TextField(help_text="Context of how this skill was demonstrated")
    score = models.IntegerField(blank=True, null=True, help_text="Optional quantitative score (0-100) from this evidence")
    confidence = models.IntegerField(default=50, help_text="0-100 confidence in this piece of evidence")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.skill.name} via {self.source_type}"


class UserSkillProficiency(models.Model):
    """Calculated current proficiency of a user in a canonical skill."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_proficiencies')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_proficiencies')
    proficiency_score = models.IntegerField(default=0, help_text="Overall calculated score (0-100)")
    confidence = models.IntegerField(default=0, help_text="Overall confidence in this score (0-100)")
    evidence_count = models.IntegerField(default=0)
    last_evaluated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'skill']
        verbose_name_plural = "User skill proficiencies"
        ordering = ['-proficiency_score']

    def __str__(self):
        return f"{self.user.email} - {self.skill.name} ({self.proficiency_score}%)"

    @property
    def skill_name(self):
        return self.skill.name

    @property
    def skill_score(self):
        return self.proficiency_score
