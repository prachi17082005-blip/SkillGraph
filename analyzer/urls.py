
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dependency_list, name='dependency_list'),
    path('add/', views.add_dependency, name='add_dependency'),
    path('skill-gap/', views.skill_gap_analyzer, name='skill_gap_analyzer'),
    path('download-career-report/', views.download_career_report, name='download_career_report'),

    path('career-comparison/', views.career_comparison, name='career_comparison'),
]
