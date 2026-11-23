
from django.db import models
from skills.models import Skill
from django.contrib.auth.models import User


class SkillDependency(models.Model):

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='dependencies'
    )

    prerequisite = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='required_for'
    )

    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.prerequisite} → {self.skill}"


class CareerRole(models.Model):

    role_name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.role_name


class RequiredSkill(models.Model):

    career = models.ForeignKey(
        CareerRole,
        on_delete=models.CASCADE,
        related_name='required_skills'
    )

    skill_name = models.CharField(max_length=100)

    importance = models.CharField(
        max_length=20,
        choices=[
            ('Basic', 'Basic'),
            ('Important', 'Important'),
            ('Essential', 'Essential'),
        ],
        default='Important'
    )

    def __str__(self):
        return f"{self.skill_name} - {self.career.role_name}"
