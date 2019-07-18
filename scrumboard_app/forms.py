from django import forms
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class AddColumnForm(forms.Form):

    nomeColonna = forms.CharField(max_length=30, required=True, label='Nome')
    boardParent = forms.ChoiceField(widget=forms.Select, label="Board di appartenenza")


class AddCardForm(forms.Form):
    nomeCard = forms.CharField(max_length=30, required=True, label='Titolo')
    descCard = forms.CharField(widget=forms.Textarea, required=True, label='Descrizione')
    dataCard = forms.DateField(widget=DateInput(), required=True, label='Data di Scadenza')
    colonnaParent = forms.ChoiceField(widget=forms.Select, label="Colonna di appartenenza")

class ModifyCardForm(forms.Form):
    nomeCard = forms.CharField(max_length=30, required=True, label='Titolo')
    descCard = forms.CharField(widget=forms.Textarea, required=True, label='Descrizione')
    dataCard = forms.DateField(widget=DateInput(), required=True, label='Data di Scadenza')
    colonnaParent = forms.ChoiceField(widget=forms.Select, label="Colonna di appartenenza")
    storyPoint = forms.IntegerField(max_value=10, min_value=0, required=True, label="Story Point")

class ModifyColumnForm(forms.Form):
    nomeColonna = forms.CharField(max_length=30, required=True, label='Nome')


class BoardForm(forms.Form):
    nomeBoard = forms.CharField(max_length=30, required=True, label='Nome')


class LoginForm(forms.Form):

    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=30, required=True)


class RegisterForm(forms.Form):

    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=30, required=True)
    conferma_password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=30, required=True)


class DeleteUserForm(forms.Form):
    utentiAssociati = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple, label='Utenti associati')


class AddUserForm(forms.Form):
    utentiRegistrati = forms.ChoiceField(required=False, widget=forms.Select, label='Aggiungi Utente')


class DeleteCardForm(forms.Form):
    cardAssociate = forms.ChoiceField(required=False, widget=forms.Select, label='Card associate alla colonna')


class AddCardToColForm(forms.Form):
    cardEsistenti = forms.ChoiceField(required=False, widget=forms.Select, label='Aggiungi Card')