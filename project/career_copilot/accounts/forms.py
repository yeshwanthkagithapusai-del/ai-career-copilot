"""
Forms for accounts app - signup, login, profile forms.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User, UserProfile


class SignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}))
    college = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'College Name'}))
    degree = forms.ChoiceField(choices=UserProfile.DEGREE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    branch = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Computer Science'}))
    academic_year = forms.ChoiceField(choices=UserProfile.YEAR_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    career_goal = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Data Scientist'}))
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password (min 8 chars)'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                college=self.cleaned_data.get('college', ''),
                degree=self.cleaned_data.get('degree', 'btech'),
                branch=self.cleaned_data.get('branch', ''),
                academic_year=self.cleaned_data.get('academic_year', '1'),
                career_goal=self.cleaned_data.get('career_goal', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}))
    password = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'college', 'degree', 'branch', 'academic_year', 'career_goal', 'profile_image', 'bio']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'college': forms.TextInput(attrs={'class': 'form-input'}),
            'degree': forms.Select(attrs={'class': 'form-input'}),
            'branch': forms.TextInput(attrs={'class': 'form-input'}),
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'career_goal': forms.TextInput(attrs={'class': 'form-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}))


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New Password'})
    new_password2 = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm New Password'})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New Password'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm New Password'})
