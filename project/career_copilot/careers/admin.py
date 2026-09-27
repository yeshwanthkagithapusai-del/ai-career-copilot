from django.contrib import admin
from .models import CareerRole, CareerRoleSkillRequirement, UserCareerGoal


class CareerRoleSkillRequirementInline(admin.TabularInline):
    model = CareerRoleSkillRequirement
    extra = 1


@admin.register(CareerRole)
class CareerRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [CareerRoleSkillRequirementInline]


@admin.register(CareerRoleSkillRequirement)
class CareerRoleSkillRequirementAdmin(admin.ModelAdmin):
    list_display = ('role', 'skill', 'priority')
    list_filter = ('priority', 'role')
    search_fields = ('role__name', 'skill__name')


@admin.register(UserCareerGoal)
class UserCareerGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_role', 'target_title', 'target_company')
    search_fields = ('user__email', 'user__username', 'target_title', 'target_company')
