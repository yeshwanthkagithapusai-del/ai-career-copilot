"""Admin registration for roadmaps app."""
from django.contrib import admin
from .models import Roadmap, Skill, PhaseTraining


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_career', 'experience_level', 'progress', 'learning_progress', 'created_at']
    list_filter = ['experience_level']
    search_fields = ['user__email', 'target_career']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_name', 'skill_score', 'source', 'updated_at']
    list_filter = ['source']
    search_fields = ['user__email', 'skill_name']


@admin.register(PhaseTraining)
class PhaseTrainingAdmin(admin.ModelAdmin):
    list_display = ['roadmap', 'phase_name', 'phase_index', 'score', 'passed', 'attempt', 'created_at']
    list_filter = ['passed']
    search_fields = ['roadmap__user__email', 'phase_name']
