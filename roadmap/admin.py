
from django.contrib import admin
from .models import LearningRoadmap, RoadmapStep


class RoadmapStepInline(admin.TabularInline):
    model = RoadmapStep
    extra = 1


@admin.register(LearningRoadmap)
class LearningRoadmapAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'career_goal',
        'user',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active', 'career_goal', 'created_at')

    search_fields = ('title', 'career_goal', 'user__username')

    inlines = [RoadmapStepInline]


@admin.register(RoadmapStep)
class RoadmapStepAdmin(admin.ModelAdmin):
    list_display = (
        'skill_name',
        'roadmap',
        'level',
        'duration_days',
        'status',
        'order',
    )

    list_filter = ('level', 'status')

    search_fields = ('skill_name', 'roadmap__title')

