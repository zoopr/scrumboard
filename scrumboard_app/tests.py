from django.test import TestCase, SimpleTestCase
from django.test import Client
from .models import *

import datetime

# Model Unit tests

class ScrumUserTestCase(TestCase):
    def setUp(self):
        ScrumUser.objects.create(username="test_user", password="test_pass")
        ScrumUser.objects.create(username="test_user2", password="test_pass2")

    def test_user_fields(self):
        u = ScrumUser.objects.get(username="test_user")
        self.assertNotEqual(u.password, "")

class BoardTestCase(TestCase):
    def setUp(self):
        ScrumUser.objects.create(username="test_user", password="test_pass")
        Board.objects.create(nome="test_board")
        Colonna.objects.create(nome="test_col1", boardParent=Board.objects.get(nome="test_board"))
        Colonna.objects.create(nome="test_col2", boardParent=Board.objects.get(nome="test_board"))
        Card.objects.create(colonnaParent=Colonna.objects.get(nome="test_col1"), titolo="test_card",
                            descrizione="test_desc", dataScadenza=datetime.date.today(), storyPoint="0")

    def test_board_fields(self):
        b = Board.objects.get(nome="test_board")
        b.utentiAssociati.add(ScrumUser.objects.get(username="test_user"))
        b.save()

        b = Board.objects.get(nome="test_board")
        self.assertEqual(b.nome, "test_board")
        self.assertEqual(len(b.utentiAssociati.all()), 1)
        self.assertEqual(b.utentiAssociati.all()[0].username, "test_user")

    def test_get_colonne(self):
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.getColonneBoard()), 2)
        self.assertEqual(b.getColonneBoard()[0].nome, "test_col1")

    def test_crea_colonna(self):
        b = Board.objects.get(nome="test_board")
        b.creaColonna("test_col3")
        self.assertEqual(b.getColonneBoard()[2].nome, "test_col3")

    def test_modifica_colonna(self):
        b = Board.objects.get(nome="test_board")
        self.assertEqual(b.getColonneBoard()[1].nome, "test_col2")
        b.modificaColonna("test_col2", "test_col_2")
        self.assertEqual(b.getColonneBoard()[1].nome, "test_col_2")

    def test_muovi_card(self):
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.getColonneBoard()[0].getCardColonna()), 1)
        self.assertEqual(len(b.getColonneBoard()[1].getCardColonna()), 0)
        self.assertEqual(b.getColonneBoard()[0].getCardColonna()[0].titolo, "test_card")
        b.muoviCard("test_col1", "test_col2", "test_card")
        self.assertEqual(len(b.getColonneBoard()[1].getCardColonna()), 1)
        self.assertEqual(len(b.getColonneBoard()[0].getCardColonna()), 0)
        self.assertEqual(b.getColonneBoard()[1].getCardColonna()[0].titolo, "test_card")

    def test_lista_utenti_associati(self):
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.utentiAssociati.all()), 0)

        b.utentiAssociati.add(ScrumUser.objects.get(username="test_user"))
        b.save()

        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.listaUtentiAssociati()), 1)
        self.assertEqual(b.listaUtentiAssociati()[0].username, "test_user")

class ColonnaTestCase(TestCase):
    def setUp(self) -> None:
        ScrumUser.objects.create(username="test_user", password="test_pass")
        Board.objects.create(nome="test_board")
        Colonna.objects.create(nome="test_col1", boardParent=Board.objects.get(nome="test_board"))
        Colonna.objects.create(nome="test_col2", boardParent=Board.objects.get(nome="test_board"))
        Card.objects.create(colonnaParent=Colonna.objects.get(nome="test_col1"), titolo="test_card1",
                            descrizione="test_desc", dataScadenza=datetime.date.today(), storyPoint="0")
        Card.objects.create(colonnaParent=Colonna.objects.get(nome="test_col1"), titolo="test_card2",
                            descrizione="test_desc", dataScadenza=datetime.date.today(), storyPoint="3")

    def test_colonna_fields(self):
        c = Colonna.objects.get(nome="test_col1")

        self.assertEqual(c.nome, "test_col1")
        self.assertEqual(c.boardParent.nome, "test_board")

    def test_get_card_colonna(self):
        c = Colonna.objects.get(nome="test_col1")

        self.assertEqual(len(c.getCardColonna()), 2)
        self.assertEqual(c.getCardColonna()[0].titolo, "test_card1")
        self.assertEqual(c.getCardColonna()[1].storyPoint, 3)

    def test_crea_card(self):
        c = Colonna.objects.get(nome="test_col1")
        self.assertEqual(len(c.getCardColonna()), 2)
        c.creaCard("test_card3", "test_desc", datetime.date.today(), 5, [])
        self.assertEqual(len(c.getCardColonna()), 3)
        self.assertEqual(c.getCardColonna()[2].titolo, "test_card3")

    def test_elimina_card(self):
        c = Colonna.objects.get(nome="test_col1")
        self.assertEqual(len(c.getCardColonna()), 2)
        c.eliminaCard("test_card2")
        self.assertEqual(len(c.getCardColonna()), 1)

    def test_modifica_card(self):
        c = Colonna.objects.get(nome="test_col1")
        self.assertEqual(c.getCardColonna()[0].titolo, "test_card1")
        self.assertEqual(c.getCardColonna()[0].descrizione, "test_desc")
        self.assertEqual(c.getCardColonna()[0].dataScadenza, datetime.date.today())
        self.assertEqual(c.getCardColonna()[0].storyPoint, 0)
        c.modificaCard("test_card1", "test_card_1", "test_desc_1", datetime.date(day=5, month=5, year=2020), 2)
        self.assertEqual(c.getCardColonna()[0].titolo, "test_card_1")
        self.assertEqual(c.getCardColonna()[0].descrizione, "test_desc_1")
        self.assertEqual(c.getCardColonna()[0].dataScadenza, datetime.date(day=5, month=5, year=2020))
        self.assertEqual(c.getCardColonna()[0].storyPoint, 2)

class CardTestCase(TestCase):
    def setUp(self) -> None:
        ScrumUser.objects.create(username="test_user", password="test_pass")
        Board.objects.create(nome="test_board")
        Colonna.objects.create(nome="test_col1", boardParent=Board.objects.get(nome="test_board"))
        Colonna.objects.create(nome="test_col2", boardParent=Board.objects.get(nome="test_board"))
        Card.objects.create(colonnaParent=Colonna.objects.get(nome="test_col1"), titolo="test_card1",
                            descrizione="test_desc", dataScadenza=datetime.date.today(), storyPoint="0")
        Card.objects.create(colonnaParent=Colonna.objects.get(nome="test_col1"), titolo="test_card2",
                            descrizione="test_desc", dataScadenza=datetime.date.today(), storyPoint="3")

    def test_card_fields(self):
        c = Card.objects.get(titolo="test_card2")

        self.assertEqual(c.titolo, "test_card2")
        self.assertEqual(c.descrizione, "test_desc")
        self.assertEqual(c.dataScadenza, datetime.date.today())
        self.assertEqual(c.storyPoint, 3)

        c.utentiCard.add(ScrumUser.objects.get(username="test_user"))
        c.save()

        c = Card.objects.get(titolo="test_card2")
        self.assertEqual(len(c.utentiCard.all()), 1)
        self.assertEqual(c.utentiCard.all()[0].username, "test_user")

# View Acceptance Test

class AcceptanceTestCase(TestCase):
    def setUp(self) -> None:
        self.client.post('/register/',
                         {"username": "test_user", "password": "test_pass", "conferma_password": "test_pass"})
        self.client.post('/add_board/', {'nomeBoard': "test_board"})
        self.client.post('/add_column/', {'nomeColonna': 'test_col', 'boardParent': '0'})
        self.client.logout()
        self.client.post('/register/',
                         {"username": "collab_user", "password": "collab_pass", "conferma_password": "collab_pass"})
        self.client.logout()

    def test_login_failure(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "fail_pass"}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_ok(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        response = self.client.post('/logout', follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register(self):
        response = self.client.post('/register/', {"username": "test_user2", "password": "test_pass2", "conferma_password": "test_pass2"})
        response = self.client.post('/login/', {"username": "test_user2", "password": "test_pass2"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_dashboard(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        response = self.client.get('/dashboard/', follow=True)
        self.assertContains(response, "Le tue Board")
        self.assertContains(response, "test_board")

    def test_add_board(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        response = self.client.post('/add_board/', {'nomeBoard': "test_board2"})
        response = self.client.get('/dashboard/', follow=True)
        self.assertContains(response, "test_board2")

    def test_add_column(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        response = self.client.post('/add_column/', {'nomeColonna': 'test_col2', 'boardParent': '0'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_col2")

    def test_add_card(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        url = '/add_card/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.post(url, {'nomeCard': "test_card", "descCard": "test_desc",
                                          "dataCard": str(datetime.date.today()), "colonnaParent": '0'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_card")

    def test_add_user(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        url = '/add_user/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.post(url, {"utentiRegistrati": '0'})
        response = self.client.get(url)
        # Collab_user non appare nella lista di utenti associabili
        self.assertNotContains(response, "<option value=\"0\">collab_user")
        response = self.client.post(url, {"utentiAssociati": '1'})
        response = self.client.get(url)
        # Collab_user appare nella lista di utenti associabili
        self.assertContains(response, "<option value=\"0\">collab_user")

'''
urlpatterns = [
    url(r'^edit_column/(?P<board_id>[0-9]+)/(?P<col_name>.+)/$', views.editColumn, name='edit_column'),
    url(r'^edit_card/(?P<board_id>[0-9]+)/(?P<col_name>.+)/(?P<card_name>.+)/$', views.editCard, name='edit_card'),
    url(r'^board/(?P<board_id>[0-9]+)/$', views.board_details, name='board_details'),
    url(r'^burndown/(?P<board_id>[0-9]+)/$', views.burndown, name='burndown'),
]'''