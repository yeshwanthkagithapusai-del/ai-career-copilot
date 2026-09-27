"""URL routes for assessments app."""
from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.test_setup, name='test_setup'),
    path('start/', views.start_test, name='start_test'),
    path('room/<int:test_id>/', views.test_room, name='test_room'),
    path('room/<int:test_id>/submit/', views.submit_test, name='submit_test'),
    path('analysis/<int:test_id>/', views.test_analysis, name='test_analysis'),
    path('history/', views.test_history, name='test_history'),
]
