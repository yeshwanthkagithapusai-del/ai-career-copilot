"""URL routes for career progress app."""
from django.urls import path
from . import views

app_name = 'career_progress'

urlpatterns = [
    path('', views.career_progress_view, name='career_progress'),
    path('data/', views.progress_data, name='progress_data'),
]
