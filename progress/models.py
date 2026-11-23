
from django.db import models
from django.contrib.auth.models import User
from roadmap.models import LearningRoadmap, RoadmapStep


class LearningProgress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_progress'
    )

    roadmap = models.ForeignKey(
        LearningRoadmap,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    step = models.ForeignKey(
        RoadmapStep,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
        ],
        default='Pending'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'step')

    def __str__(self):
        return f"{self.user.username} - {self.step.skill_name}"
