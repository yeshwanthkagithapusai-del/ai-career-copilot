from django.contrib import admin
from .models import Skill, SkillAlias, SkillEvidence, UserSkillProficiency


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'normalized_name', 'category', 'created_at')
    search_fields = ('name', 'normalized_name')
    list_filter = ('category',)


@admin.register(SkillAlias)
class SkillAliasAdmin(admin.ModelAdmin):
    list_display = ('name', 'canonical_skill')
    search_fields = ('name', 'canonical_skill__name')


@admin.register(SkillEvidence)
class SkillEvidenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'source_type', 'score', 'confidence', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'skill__name', 'source_reference')


@admin.register(UserSkillProficiency)
class UserSkillProficiencyAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency_score', 'confidence', 'evidence_count', 'last_evaluated')
    list_filter = ('last_evaluated',)
    search_fields = ('user__email', 'user__username', 'skill__name')
