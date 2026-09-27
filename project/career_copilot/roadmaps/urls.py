"""URL routes for roadmaps app."""
from django.urls import path
from . import views

app_name = 'roadmaps'

urlpatterns = [
    path('guidance/', views.course_guidance, name='course_guidance'),
    path('roadmap/', views.roadmap_view, name='roadmap'),
    path('generate/', views.generate_roadmap, name='generate_roadmap'),
    path('roadmap/<int:roadmap_id>/update-phase/', views.update_phase_status, name='update_phase'),
    path('skills/', views.skills_view, name='skills'),
    # Phase Training
    path('roadmap/<int:roadmap_id>/phase/<int:phase_index>/train/', views.start_phase_training, name='start_phase_training'),
    path('phase-training/<int:pt_id>/', views.phase_training_room, name='phase_training_room'),
    path('phase-training/<int:pt_id>/submit/', views.submit_phase_training, name='submit_phase_training'),
    path('phase-training/<int:pt_id>/result/', views.phase_training_result, name='phase_training_result'),
]
