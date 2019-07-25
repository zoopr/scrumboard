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


# Landing page. Check if a valid session cookie exists, prompt to login if it doesn't
def index(request):
    if request.user.is_authenticated:  # Redirect se l'utente è loggato
        return redirect('dashboard')
    else:
        return redirect('login')


# Main page for authenticated user. Lists all Boards owned by the user.
def dashboard(request):
    if request.user.is_authenticated:
        utenteCorrente = ScrumUser.objects.get(username=request.user.username)
        attrs = []
        listaBoard = Board.objects.filter(utentiAssociati=utenteCorrente)
        # Generate attributes to send to the template
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
        # If form is valid, check inserted data
        form = LoginForm(request.POST)
        if form.is_valid() is True:
            un = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            user = authenticate(request, username=un, password=pw)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
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
            # Add board only if name is not already present
            if not Board.objects.filter(nome=form.cleaned_data['nomeBoard']).exists():
                b = Board(nome=form.cleaned_data['nomeBoard'])
                b.save()
                b.utentiAssociati.add(request.user)
                b.save()
                return redirect('dashboard')
            else:
                form.add_error(None, "Board dallo stesso nome già presente")
    else:
        form = BoardForm()
    return render(request, "scrumboard_app/add_board.html", {'form': form})


def registerView(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['conferma_password'] \
                and not ScrumUser.objects.filter(username=form.cleaned_data['username']).exists():
            # Add new user on unique username and correctly inserted password
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

    # Generate attributes
    cardNum = 0
    colonne = []
    scadute = 0
    ps = 0

    for colonna in b.getColonneBoard():

        cards = colonna.getCardColonna().all()
        # Column-specific object
        colDict = {
            'nome': colonna.nome,
            'cardNum': len(cards)
        }
        cardNum += len(cards)
        for card in cards:
            if card.dataScadenza < datetime.date.today():
                scadute += 1
            ps += card.storyPoint
        colonne.append(colDict)
    # board-specific object
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

    # Generate attribute dictionaries
    attrs = {
        'id': board_id,
        'nome': b.nome,
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
    # Validate an incoming post request, and if usccessful create column
    if request.method == "POST":
        form = AddColumnForm(request.POST)
        form.fields['boardParent'].choices = boardAssociate
        if form.is_valid() is True:
            # If the parent board doesn't have a column with the same name, create and save object.
            b = Board.objects.get(nome=nomiAssociati[int(form.cleaned_data['boardParent'])])
            if not b.getColonneBoard().filter(nome=form.cleaned_data['nomeColonna']).exists():
                b.creaColonna(form.cleaned_data['nomeColonna'])
                return redirect('board_details', board_id=b.id)
            else:
                form.add_error(None, "Colonna dello stesso nome già presente nella board")
    else:
        # Display regular page on GET request.
        form = AddColumnForm()
        form.fields['boardParent'].choices = boardAssociate
    return render(request, "scrumboard_app/add_column.html", {'form': form})


def addCard(request, board_id):
    board = Board.objects.get(id=board_id)

    if auth_check(board, request.user) is False:
        return redirect('index')

    # Generate dropdown menu list for column.
    nomiAssociati = [c.nome for c in board.getColonneBoard()]
    colonneAssociate = zip(range(len(nomiAssociati)), nomiAssociati)
    # Process incoming POST request.
    if request.method == "POST":
        form = AddCardForm(request.POST)
        form.fields['colonnaParent'].choices = colonneAssociate
        if form.is_valid() is True:
            # Only allow creating a new card if there isn't one with the same name on the board.
            listaCard = []
            for col in board.getColonneBoard():
                listaCard.extend([card.titolo for card in col.getCardColonna()])
            if not form.cleaned_data['nomeCard'] in listaCard:
                col = board.getColonneBoard().get(nome=nomiAssociati[int(form.cleaned_data['colonnaParent'])])
                col.creaCard(form.cleaned_data['nomeCard'], form.cleaned_data['descCard'],
                             form.cleaned_data['dataCard'], 0, [request.user])
                return redirect('board_details', board_id=board.id)
            else:
                form.add_error(None, "Card dello stesso nome già presente nella board")
    else:
        # Show regular page on GET request
        form = AddCardForm()
        form.fields['colonnaParent'].choices = colonneAssociate
    return render(request, "scrumboard_app/add_card.html", {'form': form})


def addUser(request, board_id):
    board = Board.objects.get(id=board_id)

    if auth_check(board, request.user) is False:
        return redirect('index')

    # Generate dropdown lists of already collaborating users, and everyone else.
    nomiAssociati = [u for u in board.listaUtentiAssociati()]
    utentiAssociati = zip(range(len(nomiAssociati)), nomiAssociati)

    nomiRegistrati = [u.username for u in ScrumUser.objects.all()]

    for uname in nomiAssociati:
        if uname.username in nomiRegistrati:
            nomiRegistrati.remove(uname.username)

    utentiRegistrati = zip(range(len(nomiRegistrati)), nomiRegistrati)

    if request.method == "POST":
        success = False
        # DeleteUserForm
        del_form = DeleteUserForm(request.POST)
        del_form.fields['utentiAssociati'].choices = utentiAssociati
        if del_form.is_valid() is True and len(del_form.cleaned_data['utentiAssociati']) > 0:
            # Pass users to be removed from board from a valid multiple choice menu
            for uid in del_form.cleaned_data['utentiAssociati']:
                u = ScrumUser.objects.get(username=nomiAssociati[int(uid)])
                board.utentiAssociati.remove(u)
            board.save()
            success = True

        # AddUserForm
        add_form = AddUserForm(request.POST)
        add_form.fields['utentiRegistrati'].choices = utentiRegistrati
        if add_form.is_valid() is True and len(add_form.cleaned_data['utentiRegistrati']) > 0:
            print(add_form.cleaned_data['utentiRegistrati'])
            u = ScrumUser.objects.get(username=nomiRegistrati[int(add_form.cleaned_data['utentiRegistrati'])])
            board.utentiAssociati.add(u)
            board.save()
            success = True
        # Return to the board details page if at least one of these operations was taken.
        if success is True:
            return redirect('board_details', board_id=board.id)
    else:
        # Generate dropdown menus for the template on GET request.
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

    # Generate list of cards in the column
    nomiCard = [c.titolo for c in colonna.getCardColonna()]
    cardAssociate = zip(range(len(nomiCard)), nomiCard)

    # Gen list of every other card on the board.
    nomiCardBoard = []
    for col in board.getColonneBoard():
        nomiCardBoard.extend([c.titolo for c in col.getCardColonna()])
    for cardPresente in nomiCard:
        if cardPresente in nomiCardBoard:
            nomiCardBoard.remove(cardPresente)
    cardBoard = zip(range(len(nomiCardBoard)), nomiCardBoard)

    if request.method == "POST":
        success = False
        # field_form
        field_form = ModifyColumnForm(request.POST)
        if field_form.is_valid() is True:
            # Only edit if column name is unique in the board.
            if not board.getColonneBoard().filter(nome=field_form.cleaned_data['nomeColonna']).exists():
                board.modificaColonna(colonna.nome, field_form.cleaned_data['nomeColonna'])
                success = True
            else:
                field_form.add_error(None, "Colonna dallo stesso nome già presente nella board")
        # add_card_form
        add_card_form = AddCardToColForm(request.POST)
        add_card_form.fields['cardEsistenti'].choices = cardBoard
        if add_card_form.is_valid() is True and len(add_card_form.cleaned_data['cardEsistenti']) > 0:
            # Fetch correct card, and set card parent as current column.
            titolo = nomiCardBoard[int(add_card_form.cleaned_data['cardEsistenti'])]
            for col in board.getColonneBoard():
                if col.getCardColonna().filter(titolo=titolo).exists():
                    board.muoviCard(col.nome, colonna.nome, titolo)
                    break
                    # This card will always exist.
            success = True
        # del_card_form
        del_card_form = DeleteCardForm(request.POST)
        del_card_form.fields['cardAssociate'].choices = cardAssociate
        if del_card_form.is_valid() is True and len(del_card_form.cleaned_data['cardAssociate']) > 0:
            # Delete card in this column
            titolo = nomiCard[int(del_card_form.cleaned_data['cardAssociate'])]
            colonna.eliminaCard(titolo)
            success = True
        if success is True:
            # If at least one of these operations was taken successfully, return to board details.
            return redirect('board_details', board_id=board.id)
    else:
        # load necessary data for GET request template.
        field_form = ModifyColumnForm()
        field_form.initial['nomeColonna'] = colonna.nome
        add_card_form = AddCardToColForm()
        add_card_form.fields['cardEsistenti'].choices = cardBoard
        del_card_form = DeleteCardForm()
        del_card_form.fields['cardAssociate'].choices = cardAssociate
    return render(request, "scrumboard_app/modify_column.html",
                  {'field_form': field_form, 'add_card_form': add_card_form, 'del_card_form': del_card_form})


def editCard(request, board_id, col_name, card_name):
    board = Board.objects.get(id=board_id)
    colonna = board.getColonneBoard().get(nome=col_name)
    card = colonna.getCardColonna().get(titolo=card_name)

    if auth_check(board, request.user) is False:
        return redirect('index')

    # Generate list of available columns
    nomiColonne = [c.nome for c in board.getColonneBoard()]
    colonneParent = zip(range(len(nomiColonne)), nomiColonne)

    # Generate list of board-owning users assigned to the task
    nomiUtenti = [u.username for u in card.utentiCard.all()]
    utentiAssociati = zip(range(len(nomiUtenti)), nomiUtenti)

    # Generate list of board-owning users not assigned to the card.
    nomiUtentiNonAssociati = [u.username for u in ScrumUser.objects.all()]
    for utente in nomiUtenti:
        if utente in nomiUtentiNonAssociati:
            nomiUtentiNonAssociati.remove(utente)
    utentiNonAssociati = zip(range(len(nomiUtentiNonAssociati)), nomiUtentiNonAssociati)

    if request.method == "POST":
        success = False
        # field_form
        field_form = ModifyCardForm(request.POST)
        field_form.fields['colonnaParent'].choices = colonneParent
        if field_form.is_valid() is True:
            # IF there is a card on the board with the same name (except itself), fail.
            listaCard = []
            for col in board.getColonneBoard():
                listaCard.extend([card.titolo for card in col.getCardColonna().exclude(id=card.id)])
            if not field_form.cleaned_data['nomeCard'] in listaCard:
                # Update card info.
                colonna.modificaCard(card.titolo, field_form.cleaned_data['nomeCard'],
                                     field_form.cleaned_data['descCard'], field_form.cleaned_data['dataCard'],
                                     field_form.cleaned_data['storyPoint'])
                card_name = field_form.cleaned_data['nomeCard']
                # Reload card
                card = colonna.getCardColonna().get(titolo=card_name)
                card.colonnaParent = board.getColonneBoard()\
                    .get(nome=nomiColonne[int(field_form.cleaned_data['colonnaParent'])])
                card.save()
                success = True
            else:
                field_form.add_error(None, "Card dello stesso nome già presente nella board")
        # add_user_form
        add_user_form = AddUserForm(request.POST)
        add_user_form.fields['utentiRegistrati'].choices = utentiNonAssociati
        if add_user_form.is_valid() is True and len(add_user_form.cleaned_data['utentiRegistrati']) > 0:
            # Associate user with card
            user = ScrumUser.objects\
                .get(username=nomiUtentiNonAssociati[int(add_user_form.cleaned_data['utentiRegistrati'])])
            card.utentiCard.add(user)
            card.save()
            success = True
        # del_user_form
        del_user_form = DeleteUserForm(request.POST)
        del_user_form.fields['utentiAssociati'].choices = utentiAssociati
        if del_user_form.is_valid() is True and len(del_user_form.cleaned_data['utentiAssociati']) > 0:
            # Remove associated user from card
            for uid in del_user_form.cleaned_data['utentiAssociati']:
                user = ScrumUser.objects.get(username=nomiUtenti[int(uid)])
                card.utentiCard.remove(user)
                card.save()
                success = True
        if success is True:
            return redirect('board_details', board_id=board.id)
    else:
        # Create data for template, set current values as default.
        field_form = ModifyCardForm()
        field_form.fields['colonnaParent'].choices = colonneParent
        field_form.initial['nomeCard'] = card.titolo
        field_form.initial['descCard'] = card.descrizione
        field_form.initial['dataCard'] = card.dataScadenza
        field_form.initial['storyPoint'] = card.storyPoint
        field_form.initial['colonnaParent'] = nomiColonne.index(card.colonnaParent.nome)
        add_user_form = AddUserForm()
        add_user_form.fields['utentiRegistrati'].choices = utentiNonAssociati
        del_user_form = DeleteUserForm()
        del_user_form.fields['utentiAssociati'].choices = utentiAssociati
    return render(request, "scrumboard_app/modify_card.html",
                  {'field_form': field_form, 'add_user_form': add_user_form, 'del_user_form': del_user_form})
