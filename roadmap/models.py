
from django.db import models
from django.contrib.auth.models import User


class LearningRoadmap(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_roadmaps'
    )

    title = models.CharField(max_length=200)

    career_goal = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class RoadmapStep(models.Model):

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    roadmap = models.ForeignKey(
        LearningRoadmap,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    skill_name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='Beginner'
    )

    duration_days = models.PositiveIntegerField(default=7)

    order = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ('roadmap', 'order')

    def __str__(self):
        return f"{self.skill_name} - {self.roadmap.title}"

