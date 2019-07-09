from django import forms
from .models import ScrumUser


class LoginForm(forms.Form):

    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True)


class RegisterForm(forms.ModelForm):

    class Meta:
        model = ScrumUser
        fields = ('username', 'password',)
