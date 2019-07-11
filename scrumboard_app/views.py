from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from .models import *

# Create your views here.


def index(request):
    if request.user.is_authenticated:  # Redirect se l'utente è loggato
        return redirect('dashboard')
    else:
        return redirect('login')


def dashboard(request):
    if request.user.is_authenticated:
        utenteCorrente = ScrumUser.objects.get(username=request.user.username)
        attrs = []
        listaBoard = Board.objects.filter(utentiAssociati=utenteCorrente)
        for board in listaBoard:
            colonne = board.getColonneBoard()
            numcard = 0
            for colonna in colonne:
                numcard += len(colonna.getCardColonna())
            attrs.append({
                        'id': board.id,
                        'nome': board.nome,
                        'numCard': numcard
            })
        return render(request, "scrumboard_app/dashboard.html", {'boards': attrs})
    else:
        return redirect('login')

def loginView(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid() is True:
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            user = authenticate(request, username=un, password=pw)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                # TODO: modulo di errore vero
                form.add_error(None, "Errore di autenticazione")
    else:
        form = LoginForm()
    return render(request, "scrumboard_app/login.html", {'form': form})


def logoutView(request):
    logout(request)
    return redirect('index')


def addBoard(request):
    if request.method == "POST":
        form = BoardForm(request.POST)
        if form.is_valid() is True:
            if not Board.objects.filter(nome= form.cleaned_data['nomeBoard']).exists() :
                b = Board(nome=form.cleaned_data['nomeBoard'])
                b.save()
                b.utentiAssociati.add(request.user)
                b.save()
                return redirect('dashboard')
            else:
                # TODO: modulo di errore vero
                form.add_error(None, "Board dallo stesso nome già presente")
    else:
        form = BoardForm()
    return render(request, "scrumboard_app/add_board.html", {'form': form})


def registerView(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['conferma_password'] and not ScrumUser.objects.filter(username = form.cleaned_data['username']).exists():
            user = ScrumUser()
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password'])
            user.active = True
            user.staff = False
            user.admin = False
            user.save()
            login(request, user)
            return redirect('index')
        else:
            form.add_error(None, "Errore durante la registrazione utente.")
    else:
        form = RegisterForm()
    return render(request, "scrumboard_app/register.html", {'form': form})



def burndown(request, board_id):
    pass


def board_details(request, board_id):
    b = Board.objects.get(id=board_id)
    attrs = {
        'id': board_id,
        'nome':b.nome,
        'colonne': []
    }
    for col in b.getColonneBoard():
        dict_col = {
            'id': col.id,
            'nome': col.nome,
            'cards': []
        }
        for card in col.getCardColonna():
            dict_card = {
                'id': card.id,
                'nome': card.titolo
            }
            dict_col['cards'].append(dict_card)
        attrs['colonne'].append(dict_col)
    return render(request, "scrumboard_app/board_details.html", {'board': attrs})


def addColumn(request):
    pass


def addCard(request):
    pass

def addUser(request, board_id):
    pass

def editColumn(request, col_id):
    pass

def editCard(request, card_id):
    pass