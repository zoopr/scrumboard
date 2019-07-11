from django import forms
from .models import ScrumUser


class LoginForm(forms.Form):

    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True)


class RegisterForm(forms.Form):

    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True)
