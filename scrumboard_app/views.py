from django.shortcuts import render, redirect
from .forms import *

# Create your views here.


def index(request):
    if request.user.is_authenticated:  # Redirect se l'utente è loggato
        return redirect('dashboard')
    else:
        return redirect('login')


def dashboard(request):
    pass


def login(request):
    if request.method == "POST":
        pass  # Handle login request
    else:
        form = LoginForm()
    return render(request, "scrumboard_app/login.html", {'form': form})


def register(request):
    if request.method == "POST":
        pass  # Handle registration request
    else:
        form = RegisterForm()
    return render(request, "scrumboard_app/register.html", {'form': form})


def burndown(request, board_id):
    pass


def board_utente(request, board_id):
    pass
