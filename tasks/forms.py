from django import forms
from django.contrib.auth.models import User
from .models import Task, Profile

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'date_time', 'location', 'space', 'type', 'users', 'image']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UpdateProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number','university_career', 'profile_image']
        widgets = {
            'university_career': forms.Select(attrs={'class': 'career-select'}),
        }