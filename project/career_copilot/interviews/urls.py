"""URL routes for interviews app."""
from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.interview_setup, name='interview_setup'),
    path('start/', views.start_interview, name='start_interview'),
    path('room/<int:interview_id>/', views.interview_room, name='interview_room'),
    path('room/<int:interview_id>/submit/<int:answer_id>/', views.submit_answer, name='submit_answer'),
    path('room/<int:interview_id>/complete/', views.complete_interview, name='complete_interview'),
    path('report/<int:interview_id>/', views.interview_report, name='interview_report'),
    path('history/', views.interview_history, name='interview_history'),
]
