"""URL routes for resume analyzer app."""
from django.urls import path
from . import views

app_name = 'resume_analyzer'

urlpatterns = [
    path('', views.resume_analyzer, name='resume_analyzer'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('report/<int:resume_id>/', views.ats_report, name='ats_report'),
    path('history/', views.resume_history, name='resume_history'),
]
