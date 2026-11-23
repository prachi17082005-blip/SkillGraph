
from django.urls import path
from . import views

urlpatterns = [
    path('', views.roadmap_list, name='roadmap_list'),
    path('create/', views.create_roadmap, name='create_roadmap'),
    path('<int:roadmap_id>/add-step/', views.add_roadmap_step, name='add_roadmap_step'),
    path('step/<int:step_id>/update/', views.update_step_status, name='update_step_status'),
    path('add-recommended-skill/', views.add_recommended_skill, name='add_recommended_skill'),
]
