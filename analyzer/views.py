
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from skills.models import Skill
from .models import SkillDependency, CareerRole, RequiredSkill


# ---------------------------------
# SKILL DEPENDENCY LIST
# ---------------------------------

@login_required
def dependency_list(request):

    dependencies = SkillDependency.objects.filter(
        Q(skill__user=request.user) |
        Q(prerequisite__user=request.user)
    ).select_related(
        'skill',
        'prerequisite'
    ).distinct().order_by('id')

    return render(
        request,
        'analyzer/dependency_list.html',
        {'dependencies': dependencies}
    )


# ---------------------------------
# ADD SKILL DEPENDENCY
# ---------------------------------

@login_required
def add_dependency(request):

    skills = Skill.objects.filter(user=request.user)

    if request.method == 'POST':

        skill_value = request.POST.get('skill', '').strip()
        prerequisite_value = request.POST.get('prerequisite', '').strip()
        description = request.POST.get('description', '').strip()

        if skill_value.isdigit():
            skill = skills.filter(id=int(skill_value)).first()
        else:
            skill = skills.filter(
                skill_name__iexact=skill_value
            ).first()

        if prerequisite_value.isdigit():
            prerequisite = skills.filter(
                id=int(prerequisite_value)
            ).first()
        else:
            prerequisite = skills.filter(
                skill_name__iexact=prerequisite_value
            ).first()

        if not skill or not prerequisite:
            messages.error(request, 'Please select valid skills.')

        elif skill.id == prerequisite.id:
            messages.error(
                request,
                'A skill cannot be its own prerequisite.'
            )

        elif SkillDependency.objects.filter(
            skill=skill,
            prerequisite=prerequisite
        ).exists():
            messages.warning(
                request,
                'This dependency already exists.'
            )

        else:
            SkillDependency.objects.create(
                skill=skill,
                prerequisite=prerequisite,
                description=description
            )

            messages.success(
                request,
                'Skill dependency added successfully!'
            )

            return redirect('dependency_list')

    return render(
        request,
        'analyzer/add_dependency.html',
        {'skills': skills}
    )


# ---------------------------------
# SKILL GAP ANALYZER
# ---------------------------------

@login_required
def skill_gap_analyzer(request):

    skills = Skill.objects.filter(user=request.user)
    careers = CareerRole.objects.prefetch_related('required_skills')

    selected_role = None
    matched_skills = []
    missing_skills = []
    readiness_score = 0
    total_matched = 0
    recommendations = []
    readiness_label = ""

    if request.method == 'POST':

        career_id = request.POST.get('career')

        selected_role = get_object_or_404(
            CareerRole,
            id=career_id
        )

        user_skill_names = {
            name.lower()
            for name in skills.values_list('skill_name', flat=True)
        }

        required_skills = selected_role.required_skills.all()

        for required in required_skills:

            if required.skill_name.lower() in user_skill_names:
                matched_skills.append(required.skill_name)
            else:
                missing_skills.append(required.skill_name)

        total_matched = len(matched_skills)

        total_required = total_matched + len(missing_skills)

        if total_required > 0:
            readiness_score = round(
                (total_matched / total_required) * 100
            )

        if readiness_score >= 80:
            readiness_label = "Excellent"
        elif readiness_score >= 60:
            readiness_label = "Good"
        elif readiness_score >= 40:
            readiness_label = "Moderate"
        else:
            readiness_label = "Needs Improvement"

        recommendations = [
            {
                'skill': skill,
                'importance': 'High'
            }
            for skill in missing_skills
        ]

    return render(
        request,
        'analyzer/skill_gap.html',
        {
            'skills': skills,
            'careers': careers,
            'selected_role': selected_role,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'readiness_score': readiness_score,
            'total_matched': total_matched,
            'readiness_label': readiness_label,
            'recommendations': recommendations,
        }
    )


# ---------------------------------
# DOWNLOAD CAREER REPORT
# ---------------------------------

@login_required
def download_career_report(request):

    skills = Skill.objects.filter(user=request.user)

    career_id = request.GET.get('career')
    selected_role = None
    matched_skills = []
    missing_skills = []
    readiness_score = 0
    readiness_label = "Needs Improvement"

    if career_id:
        selected_role = get_object_or_404(
            CareerRole,
            id=career_id
        )

        user_skill_names = {
            skill.skill_name.lower()
            for skill in skills
        }

        required_skills = selected_role.required_skills.all()

        for required in required_skills:
            if required.skill_name.lower() in user_skill_names:
                matched_skills.append(required.skill_name)
            else:
                missing_skills.append(required.skill_name)

        total_required = len(matched_skills) + len(missing_skills)

        if total_required > 0:
            readiness_score = round(
                len(matched_skills) / total_required * 100
            )

        if readiness_score >= 80:
            readiness_label = "Excellent"
        elif readiness_score >= 60:
            readiness_label = "Good"
        elif readiness_score >= 40:
            readiness_label = "Moderate"

    context = {
        'user': request.user,
        'skills': skills,
        'selected_role': selected_role,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'readiness_score': readiness_score,
        'readiness_label': readiness_label,
    }

    html = render_to_string(
        'analyzer/career_report.html',
        context
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="SkillGraph_Career_Report.pdf"'
    )

    pdf_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pdf_status.err:
        return HttpResponse(
            'PDF generation failed. Please try again.'
        )

    return response



# ---------------------------------
# CAREER COMPARISON
# ---------------------------------

@login_required
def career_comparison(request):

    careers = CareerRole.objects.prefetch_related(
        'required_skills'
    )

    selected_careers = []
    comparison_results = []

    if request.method == 'POST':

        selected_ids = request.POST.getlist('careers')

        selected_careers = list(
            careers.filter(id__in=selected_ids).distinct()
        )

        user_skill_names = {
            name.lower()
            for name in Skill.objects.filter(
                user=request.user
            ).values_list('skill_name', flat=True)
        }

        if len(selected_careers) >= 2:

            for career in selected_careers:

                required_names = list(
                    career.required_skills.values_list(
                        'skill_name',
                        flat=True
                    )
                )

                matched = [
                    name for name in required_names
                    if name.lower() in user_skill_names
                ]

                missing = [
                    name for name in required_names
                    if name.lower() not in user_skill_names
                ]

                total = len(required_names)
                matched_count = len(matched)
                missing_count = len(missing)

                score = round(
                    (matched_count / total) * 100
                ) if total else 0

                comparison_results.append({
                    'career': career,
                    'score': score,
                    'readiness_score': score,
                    'total_required': total,
                    'matched_count': matched_count,
                    'missing_count': missing_count,
                    'matched_skills': matched,
                    'missing_skills': missing,
                })

    comparison_results.sort(
        key=lambda item: item['score'],
        reverse=True
    )

    context = {
        'careers': careers,
        'selected_careers': selected_careers,

        # Both template variable names are supported
        'comparison_results': comparison_results,
        'comparison_data': comparison_results,

        'selected_ids': [
            str(career.id)
            for career in selected_careers
        ],

        'is_post': request.method == 'POST',
    }

    return render(
        request,
        'analyzer/career_comparison.html',
        context
    )
