
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from django.utils import timezone

from .models import LearningRoadmap, RoadmapStep


@login_required
def roadmap_list(request):
    roadmaps = LearningRoadmap.objects.filter(
        user=request.user
    ).prefetch_related('steps')

    for roadmap in roadmaps:
        steps = list(roadmap.steps.all())

        total_steps = len(steps)
        completed_steps = sum(1 for step in steps if step.status == 'Completed')
        in_progress_steps = sum(1 for step in steps if step.status == 'In Progress')
        pending_steps = sum(1 for step in steps if step.status == 'Pending')
        total_days = sum(step.duration_days for step in steps)

        progress_percent = round(
            (completed_steps / total_steps) * 100
        ) if total_steps else 0

        roadmap.total_steps = total_steps
        roadmap.completed_steps = completed_steps
        roadmap.in_progress_steps = in_progress_steps
        roadmap.pending_steps = pending_steps
        roadmap.total_days = total_days
        roadmap.progress_percent = progress_percent

    return render(
        request,
        'roadmap/roadmap_list.html',
        {'roadmaps': roadmaps}
    )


@login_required
def create_roadmap(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        career_goal = request.POST.get('career_goal', '').strip()
        description = request.POST.get('description', '').strip()

        if not title or not career_goal:
            messages.error(request, 'Please enter all required fields.')
            return redirect('create_roadmap')

        LearningRoadmap.objects.create(
            user=request.user,
            title=title,
            career_goal=career_goal,
            description=description
        )

        messages.success(request, 'Learning roadmap created successfully!')
        return redirect('roadmap_list')

    return render(request, 'roadmap/create_roadmap.html')


@login_required
def add_roadmap_step(request, roadmap_id):
    roadmap = get_object_or_404(
        LearningRoadmap,
        id=roadmap_id,
        user=request.user
    )

    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        description = request.POST.get('description', '').strip()
        level = request.POST.get('level', 'Beginner')
        duration = request.POST.get('duration_days', '7')

        if not skill_name:
            messages.error(request, 'Please enter a skill name.')
            return redirect('add_roadmap_step', roadmap_id=roadmap.id)

        if level not in ['Beginner', 'Intermediate', 'Advanced']:
            messages.error(request, 'Invalid skill level.')
            return redirect('add_roadmap_step', roadmap_id=roadmap.id)

        try:
            duration = int(duration)
            if duration < 1:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Enter a valid duration.')
            return redirect('add_roadmap_step', roadmap_id=roadmap.id)

        last_order = roadmap.steps.aggregate(
            max_order=Max('order')
        )['max_order'] or 0

        RoadmapStep.objects.create(
            roadmap=roadmap,
            skill_name=skill_name,
            description=description,
            level=level,
            duration_days=duration,
            order=last_order + 1
        )

        messages.success(request, 'Learning step added successfully!')
        return redirect('roadmap_list')

    return render(
        request,
        'roadmap/add_roadmap_step.html',
        {'roadmap': roadmap}
    )


@login_required
def update_step_status(request, step_id):
    step = get_object_or_404(
        RoadmapStep,
        id=step_id,
        roadmap__user=request.user
    )

    if request.method == 'POST':
        status = request.POST.get('status')

        valid_statuses = ['Pending', 'In Progress', 'Completed']

        if status not in valid_statuses:
            messages.error(request, 'Invalid progress status.')
            return redirect('roadmap_list')

        step.status = status

        if status == 'Completed':
            if not step.completed_at:
                step.completed_at = timezone.now()
        else:
            step.completed_at = None

        step.save()

        messages.success(request, 'Learning progress updated successfully!')

    return redirect('roadmap_list')


@login_required
def add_recommended_skill(request):
    if request.method != 'POST':
        return redirect('skill_gap_analyzer')

    from analyzer.models import RequiredSkill

    required_skill_id = request.POST.get('required_skill_id')
    roadmap_id = request.POST.get('roadmap_id')

    roadmap = get_object_or_404(
        LearningRoadmap,
        id=roadmap_id,
        user=request.user
    )

    required_skill = get_object_or_404(
        RequiredSkill,
        id=required_skill_id
    )

    skill_name = required_skill.skill_name

    already_added = roadmap.steps.filter(
        skill_name__iexact=skill_name
    ).exists()

    if already_added:
        messages.warning(
            request,
            f'{skill_name} is already in your roadmap!'
        )
        return redirect('skill_gap_analyzer')

    last_order = roadmap.steps.aggregate(
        max_order=Max('order')
    )['max_order'] or 0

    RoadmapStep.objects.create(
        roadmap=roadmap,
        skill_name=skill_name,
        description=f'Recommended skill for {required_skill.career.role_name}',
        level='Beginner',
        duration_days=7,
        order=last_order + 1
    )

    messages.success(
        request,
        f'{skill_name} added to your learning roadmap successfully!'
    )

    return redirect('skill_gap_analyzer')
