from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class ScrumUser(AbstractUser):
    pass


class Board(models.Model):
    # Genera in automatico una primary key numerica incrementale di id.
    nome = models.CharField(max_length=30, unique=True)
    utentiAssociati = models.ManyToManyField("ScrumUser")

    def getColonneBoard(self):
        return Colonna.objects.filter(boardParent=self)

    def creaColonna(self, col_name):
        c = Colonna(boardParent=self, nome=col_name)
        c.save()

    def eliminaColonna(self, col_name):
        c = Colonna.objects.get(boardParent=self, nome=col_name)
        c.delete()

    def modificaColonna(self, col_name, new_name):
        c = Colonna.objects.get(boardParent=self, nome=col_name)
        c.nome = new_name
        c.save()

    def muoviCard(self, src_name, dest_name, card_name):
        src = Colonna.objects.get(boardParent=self, nome=src_name)
        dest = Colonna.objects.get(boardParent=self, nome=dest_name)
        card = Card.objects.get(colonnaParent=src, titolo=card_name)
        card.colonnaParent = dest
        card.save()

    def listaUtentiAssociati(self):
        return self.utentiAssociati.only("username")


class Colonna(models.Model):
    # Genera in automatico una primary key numerica incrementale di id.
    boardParent = models.ForeignKey("Board",  on_delete=models.CASCADE)
    nome = models.CharField(max_length=30)

    def getCardColonna(self):
        return Card.objects.filter(colonnaParent=self)

    def creaCard(self, card_titolo, card_desc, card_data, card_story, card_utenti):
        c = Card(colonnaParent=self, titolo=card_titolo, descrizione=card_desc, dataScadenza=card_data, storyPoint=card_story)
        c.save()
        # Card_utenti è una lista di utenti.
        for user in card_utenti:
            c.utentiCard.add(user)
        c.save()

    def eliminaCard(self, card_name):
        c = Card.objects.get(colonnaParent=self, nome=card_name)
        c.delete()

    def modificaCard(self, prev_titolo, card_titolo, card_desc, card_data, card_story, card_utenti):
        c = Card.objects.get(colonnaParent=self, titolo=prev_titolo)
        c.titolo = card_titolo
        c.descrizione = card_desc
        c.dataScadenza = card_data
        c.storyPoint = card_story
        # Resetta e aggiungi solo gli utenti sulla lista.
        c.utentiCard.clear()
        for user in card_utenti:
            c.utentiCard.add(user)
        c.save()


class Card(models.Model):
    # Genera in automatico una primary key numerica incrementale di id.
    colonnaParent = models.ForeignKey("Colonna",  on_delete=models.CASCADE)
    titolo = models.CharField(max_length=30)
    descrizione = models.TextField()
    dataScadenza = models.DateField()
    storyPoint = models.IntegerField()
    utentiCard = models.ManyToManyField("ScrumUser")
