
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Skill


@login_required
def skill_list(request):
    skills = Skill.objects.filter(user=request.user)
    return render(request, 'skills/skill_list.html', {'skills': skills})


@login_required
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        level = request.POST.get('level', '').strip()

        if not skill_name or level not in [
            'Beginner', 'Intermediate', 'Advanced'
        ]:
            messages.error(request, 'Please enter a skill and select a valid level.')
            return redirect('add_skill')

        try:
            Skill.objects.create(
                user=request.user,
                skill_name=skill_name,
                level=level
            )
            messages.success(request, 'Skill added successfully!')
            return redirect('skill_list')

        except IntegrityError:
            messages.error(request, 'Unable to save this skill.')
            return redirect('add_skill')

    return render(request, 'skills/add_skill.html')


@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(
        Skill, id=skill_id, user=request.user
    )

    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted successfully!')

    return redirect('skill_list')
