from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from .models import *

# Create your views here.
def auth_check(board, user):
    for u in board.listaUtentiAssociati():
        if user.username == u.username:
            return True
    return False

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
    board = Board.objects.get(id=board_id)

    if auth_check(board, request.user) is False:
        return redirect('index')


def board_details(request, board_id):
    b = Board.objects.get(id=board_id)

    if auth_check(b, request.user) is False:
        return redirect('index')

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
    nomiAssociati = [b.nome for b in Board.objects.filter(utentiAssociati=request.user)]
    boardAssociate = zip(range(len(nomiAssociati)), nomiAssociati)
    if request.method == "POST":
        form = AddColumnForm(request.POST)
        form.fields['boardParent'].choices = boardAssociate
        if form.is_valid() is True:
            if not Colonna.objects.filter(nome= form.cleaned_data['nomeColonna']).exists():
                c = Colonna(nome=form.cleaned_data['nomeColonna'])
                b = Board.objects.get(nome=nomiAssociati[int(form.cleaned_data['boardParent'])])
                c.boardParent = b
                c.save()
                return redirect('board_details', board_id=b.id)
            else:
                # TODO: modulo di errore vero
                form.add_error(None, "Colonna dello stesso nome già presente")
    else:
        form = AddColumnForm()
        form.fields['boardParent'].choices = boardAssociate
    return render(request, "scrumboard_app/add_column.html", {'form': form})



def addCard(request, board_id):
    board = Board.objects.get(id=board_id)


    if auth_check(board, request.user) is False:
        return redirect('index')

    nomiAssociati = [c.nome for c in board.getColonneBoard()]
    colonneAssociate = zip(range(len(nomiAssociati)), nomiAssociati)
    if request.method == "POST":
        form = AddCardForm(request.POST)
        form.fields['colonnaParent'].choices = colonneAssociate
        if form.is_valid() is True:
            if not Card.objects.filter(colonnaParent__in=board.getColonneBoard(), titolo=form.cleaned_data['nomeCard']).exists():
                card = Card(titolo=form.cleaned_data['nomeCard'], descrizione=form.cleaned_data['descCard'], dataScadenza=form.cleaned_data['dataCard'], storyPoint=0)
                col = Colonna.objects.get(boardParent=board, nome=nomiAssociati[int(form.cleaned_data['colonnaParent'])])
                print(col.nome)
                card.colonnaParent = col
                card.save()
                return redirect('board_details', board_id=board.id)
            else:
                # TODO: modulo di errore vero
                form.add_error(None, "Card dello stesso nome già presente")
    else:
        form = AddCardForm()
        form.fields['colonnaParent'].choices = colonneAssociate
    return render(request, "scrumboard_app/add_card.html", {'form': form})

def addUser(request, board_id):
    board = Board.objects.get(id=board_id)

    if auth_check(board, request.user) is False:
        return redirect('index')


    nomiAssociati = [u for u in board.listaUtentiAssociati()]
    utentiAssociati = zip(range(len(nomiAssociati)), nomiAssociati)

    nomiRegistrati = [u.username for u in ScrumUser.objects.all()]

    for uname in nomiAssociati:
        if uname in nomiRegistrati:
            nomiRegistrati.remove(uname)

    utentiRegistrati = zip(range(len(nomiRegistrati)), nomiRegistrati)

    if request.method == "POST":
        # DeleteUserForm
        del_form = DeleteUserForm(request.POST)
        del_form.fields['utentiAssociati'].choices = utentiAssociati
        if del_form.is_valid() is True and len(del_form.cleaned_data['utentiAssociati']) > 0:
            print(del_form.cleaned_data['utentiAssociati'])
            for uid in del_form.cleaned_data['utentiAssociati']:
                u = ScrumUser.objects.get(username=nomiAssociati[int(uid)])
                board.utentiAssociati.remove(u)
            board.save()
            return redirect('board_details', board_id=board.id)
        # AddUserForm
        add_form = AddUserForm(request.POST)
        add_form.fields['utentiRegistrati'].choices = utentiRegistrati
        if add_form.is_valid() is True:
            print(add_form.cleaned_data['utentiRegistrati'])
            u = ScrumUser.objects.get(username=nomiRegistrati[int(add_form.cleaned_data['utentiRegistrati'])])
            board.utentiAssociati.add(u)
            board.save()
            return redirect('board_details', board_id=board.id)
    else:
        del_form = DeleteUserForm(request.POST)
        del_form.fields['utentiAssociati'].choices = utentiAssociati
        add_form = AddUserForm(request.POST)
        add_form.fields['utentiRegistrati'].choices = utentiRegistrati
    return render(request, "scrumboard_app/add_user.html", {'add_form': add_form, 'del_form': del_form})

def editColumn(request, col_id):
    pass

def editCard(request, card_id):
    pass