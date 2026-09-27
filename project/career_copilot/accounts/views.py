"""
Views for accounts app - signup, login, logout, password reset, profile.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignupForm, LoginForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import UserProfile, Notification


def landing(request):
    """Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return render(request, 'landing.html')


def signup_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to AI Career Copilot, {user.full_name}!")
            return redirect('dashboard:dashboard')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name or user.username}!")
            next_url = request.GET.get('next', 'dashboard:dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('accounts:landing')
    return render(request, 'accounts/logout_confirm.html')


@login_required
def profile_view(request):
    """View and edit user profile."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile/profile.html', {'form': form, 'profile': profile})


@login_required
def settings_view(request):
    """User settings page."""
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'settings/settings.html', {'profile': profile})


@login_required
def notifications_view(request):
    """Get user notifications (for AJAX)."""
    notifications = Notification.objects.filter(user=request.user)[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    notifications_data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'action_url': n.action_url,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%b %d, %Y %H:%M'),
    } for n in notifications]
    
    from django.http import JsonResponse
    return JsonResponse({'notifications': notifications_data, 'unread_count': unread_count})


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    from django.http import JsonResponse
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    from django.http import JsonResponse
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
