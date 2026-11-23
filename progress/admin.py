
from django.contrib import admin
from .models import LearningProgress


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'roadmap',
        'step',
        'status',
        'updated_at',
    )

    list_filter = (
        'status',
        'updated_at',
    )

    search_fields = (
        'user__username',
        'roadmap__title',
        'step__skill_name',
    )
