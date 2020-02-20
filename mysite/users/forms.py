from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


username_regex_field = forms.RegexField (
    label = "Username",
    max_length = 30,
    regex = r"^[a-zA-Z\d\-]+$",
    error_messages={
        'invalid': ("This value must contain only letters, numbers, and hyphens.")
    }
)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = username_regex_field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = username_regex_field

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
