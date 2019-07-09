from django import forms
from .models import ScrumUser


class LoginForm(forms.ModelForm):

    class Meta:
        model = ScrumUser
        fields = ('username', 'password',)
        help_texts = {
            'username': None,
        }


class RegisterForm(forms.ModelForm):

    class Meta:
        model = ScrumUser
        fields = ('username', 'password',)