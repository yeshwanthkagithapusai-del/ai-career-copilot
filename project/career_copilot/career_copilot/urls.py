"""
URL configuration for AI Career Copilot.
"""
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static


def redirect_to_landing(request, path=None):
    return HttpResponseRedirect('/')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('resume/', include('resume_analyzer.urls')),
    path('interviews/', include('interviews.urls')),
    path('assessments/', include('assessments.urls')),
    path('roadmaps/', include('roadmaps.urls')),
    path('progress/', include('career_progress.urls')),
    path('projects/', include('projects.urls')),
    path('api/ai/', include('ai_services.urls')),
    re_path(r'^.+$', redirect_to_landing, name='fallback_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
