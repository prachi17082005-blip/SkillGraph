
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from roadmap.models import LearningRoadmap, RoadmapStep


@login_required
def progress_dashboard(request):

    roadmaps = LearningRoadmap.objects.filter(
        user=request.user
    ).prefetch_related('steps')

    total_steps = 0
    completed_steps = 0
    pending_steps = 0
    in_progress_steps = 0

    roadmap_data = []

    # Roadmap-wise progress
    for roadmap in roadmaps:

        steps = list(roadmap.steps.all())

        total = len(steps)

        completed = sum(
            1 for step in steps if step.status == 'Completed'
        )

        pending = sum(
            1 for step in steps if step.status == 'Pending'
        )

        in_progress = sum(
            1 for step in steps if step.status == 'In Progress'
        )

        percentage = round((completed / total) * 100) if total else 0

        total_steps += total
        completed_steps += completed
        pending_steps += pending
        in_progress_steps += in_progress

        roadmap_data.append({
            'roadmap': roadmap,
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'percentage': percentage,
        })

    # Overall progress
    overall_percentage = (
        round((completed_steps / total_steps) * 100)
        if total_steps else 0
    )

    # Weekly Learning Activity
    today = timezone.localdate()

    weekly_labels = []
    weekly_completed = []

    for i in range(6, -1, -1):

        day = today - timedelta(days=i)

        count = RoadmapStep.objects.filter(
            roadmap__user=request.user,
            status='Completed',
            completed_at__date=day
        ).count()

        weekly_labels.append(day.strftime('%a'))
        weekly_completed.append(count)

    # Context
    context = {
        'roadmap_data': roadmap_data,
        'total_steps': total_steps,
        'completed_steps': completed_steps,
        'pending_steps': pending_steps,
        'in_progress_steps': in_progress_steps,
        'overall_percentage': overall_percentage,

        'weekly_labels': weekly_labels,
        'weekly_completed': weekly_completed,
    }

    return render(
        request,
        'progress/progress_dashboard.html',
        context
    )
