from django.urls import path
from . import views

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('add/', views.add_skill, name='add_skill'),
    path('delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
]