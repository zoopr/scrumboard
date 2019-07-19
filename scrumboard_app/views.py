from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *

import datetime

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
    b = Board.objects.get(id=board_id)

    if auth_check(b, request.user) is False:
        return redirect('index')

    # Genera attributi
    cardNum = 0
    colonne = []
    scadute = 0
    ps= 0

    for colonna in b.getColonneBoard():

        cards = colonna.getCardColonna().all()
        dict = {
            'nome': colonna.nome,
            'cardNum': len(cards)
        }
        cardNum += len(cards)
        for card in cards:
            if card.dataScadenza < datetime.date.today():
                scadute +=1
            ps += card.storyPoint
        colonne.append(dict)

    attrs = {
        'cardNum': cardNum,
        'colonne': colonne,
        'scadute': scadute,
        'ps': ps
    }
    return render(request, "scrumboard_app/burndown.html", {'attrs': attrs})

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
                form.add_error(None, "Colonna dello stesso nome già presente nella board")
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
                card.utentiCard.add(request.user)
                card.save()
                return redirect('board_details', board_id=board.id)
            else:
                # TODO: modulo di errore vero
                form.add_error(None, "Card dello stesso nome già presente nella board")
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
        if add_form.is_valid() is True and len(add_form.cleaned_data['utentiRegistrati']) > 0:
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

def editColumn(request, board_id, col_name):
    board = Board.objects.get(id=board_id)
    colonna = board.getColonneBoard().get(nome=col_name)

    if auth_check(board, request.user) is False:
        return redirect('index')

    # Generare lista per la rimozione di card nella colonna
    nomiCard = [c.titolo for c in colonna.getCardColonna()]
    cardAssociate = zip(range(len(nomiCard)), nomiCard)

    # Generare lista per l'aggiunta di card esistenti nella board, non già appartenenti alla colonna
    nomiCardBoard = []
    for col in board.getColonneBoard():
        nomiCardBoard.extend([c.titolo for c in col.getCardColonna()])
    for cardPresente in nomiCard:
        if cardPresente in nomiCardBoard:
            nomiCardBoard.remove(cardPresente)
    cardBoard = zip(range(len(nomiCardBoard)), nomiCardBoard)

    if request.method == "POST":
        # field_form
        field_form = ModifyColumnForm(request.POST)
        if field_form.is_valid() is True:
            if not board.getColonneBoard().filter(nome=field_form.cleaned_data['nomeColonna']).exists():
                colonna.nome = field_form.cleaned_data['nomeColonna']
                colonna.save()
                return redirect('board_details', board_id=board.id)
            else:
                field_form.add_error(None, "Colonna dallo stesso nome già presente nella board")
        # add_card_form
        add_card_form = AddCardToColForm(request.POST)
        add_card_form.fields['cardEsistenti'].choices = cardBoard
        if add_card_form.is_valid() is True and len(add_card_form.cleaned_data['cardEsistenti']) > 0:
            # Estrai card, setta colonna parent come quella corrente.
            titolo = nomiCardBoard[int(add_card_form.cleaned_data['cardEsistenti'])]
            print(titolo)
            card = Card.objects.get(colonnaParent__in=board.getColonneBoard(), titolo=titolo)
            card.colonnaParent = colonna
            card.save()
            return redirect('board_details', board_id=board.id)
        # del_card_board
        del_card_form = DeleteCardForm(request.POST)
        del_card_form.fields['cardAssociate'].choices = cardAssociate
        if del_card_form.is_valid() is True and len(del_card_form.cleaned_data['cardAssociate']) > 0:
            titolo=nomiCard[int(del_card_form.cleaned_data['cardAssociate'])]
            print(titolo)
            card = colonna.getCardColonna().get(titolo=titolo)
            card.delete()
            return redirect('board_details', board_id=board.id)
    else:
        field_form = ModifyColumnForm()
        field_form.initial['nomeColonna'] = colonna.nome
        add_card_form = AddCardToColForm()
        add_card_form.fields['cardEsistenti'].choices = cardBoard
        del_card_form = DeleteCardForm()
        del_card_form.fields['cardAssociate'].choices = cardAssociate
    return render(request, "scrumboard_app/modify_column.html", {'field_form': field_form, 'add_card_form': add_card_form, 'del_card_form': del_card_form})

def editCard(request, board_id, col_name, card_name):
    board = Board.objects.get(id=board_id)
    colonna = board.getColonneBoard().get(nome=col_name)
    card = colonna.getCardColonna().get(titolo=card_name)

    if auth_check(board, request.user) is False:
        return redirect('index')

    # Generare lista di colonne a cui la card può essere aggiunta
    nomiColonne = [c.nome for c in board.getColonneBoard()]
    colonneParent = zip(range(len(nomiColonne)), nomiColonne)

    # Generare lista per la rimozione di utenti dal task della card
    nomiUtenti = [u.username for u in card.utentiCard.all()]
    utentiAssociati = zip(range(len(nomiUtenti)), nomiUtenti)

    # Generare lista per l'aggiunta di utenti registrati non partecipanti alla card.
    nomiUtentiNonAssociati = [u.username for u in ScrumUser.objects.all()]
    for utente in nomiUtenti:
        if utente in nomiUtentiNonAssociati:
            nomiUtentiNonAssociati.remove(utente)
    utentiNonAssociati = zip(range(len(nomiUtentiNonAssociati)), nomiUtentiNonAssociati)

    if request.method == "POST":
        # field_form
        field_form = ModifyCardForm(request.POST)
        field_form.fields['colonnaParent'].choices = colonneParent
        if field_form.is_valid() is True:
            if not Card.objects.filter(colonnaParent__in=board.getColonneBoard(), titolo=field_form.cleaned_data['nomeCard']).exclude(id=card.id).exists():
                card.titolo = field_form.cleaned_data['nomeCard']
                card.descrizione = field_form.cleaned_data['descCard']
                card.storyPoint = field_form.cleaned_data['storyPoint']
                card.dataScadenza = field_form.cleaned_data['dataCard']
                card.colonnaParent = board.getColonneBoard().get(nome=nomiColonne[int(field_form.cleaned_data['colonnaParent'])])
                card.save()
                return redirect('board_details', board_id=board.id)
            else:
                field_form.add_error(None, "Card dello stesso nome già presente nella board")
        # add_user_form
        add_user_form = AddUserForm(request.POST)
        add_user_form.fields['utentiRegistrati'].choices = utentiNonAssociati
        if add_user_form.is_valid() is True and len(add_user_form.cleaned_data['utentiRegistrati']) > 0:
            user = ScrumUser.objects.get(username=nomiUtentiNonAssociati[int(add_user_form.cleaned_data['utentiRegistrati'])])
            card.utentiCard.add(user)
            card.save()
            return redirect('board_details', board_id=board.id)
        # del_user_form
        del_user_form = DeleteUserForm(request.POST)
        del_user_form.fields['utentiAssociati'].choices = utentiAssociati
        if del_user_form.is_valid() is True and len(del_user_form.cleaned_data['utentiAssociati']) > 0:
            for id in del_user_form.cleaned_data['utentiAssociati']:
                user = ScrumUser.objects.get(username=nomiUtenti[int(id)])
                card.utentiCard.remove(user)
                card.save()
            return redirect('board_details', board_id=board.id)
    else:
        field_form = ModifyCardForm()
        field_form.fields['colonnaParent'].choices = colonneParent
        # Set valori correnti come default
        field_form.initial['nomeCard'] = card.titolo
        field_form.initial['descCard'] = card.descrizione
        field_form.initial['dataCard'] = card.dataScadenza
        field_form.initial['storyPoint'] = card.storyPoint
        field_form.initial['colonnaParent'] = nomiColonne.index(card.colonnaParent.nome)
        add_user_form = AddUserForm()
        add_user_form.fields['utentiRegistrati'].choices = utentiNonAssociati
        del_user_form = DeleteUserForm()
        del_user_form.fields['utentiAssociati'].choices = utentiAssociati
    return render(request, "scrumboard_app/modify_card.html", {'field_form': field_form, 'add_user_form': add_user_form, 'del_user_form': del_user_form})