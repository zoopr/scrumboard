from django.test import TestCase
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
        # Aggiungi alla board un utente associato
        b = Board.objects.get(nome="test_board")
        b.utentiAssociati.add(ScrumUser.objects.get(username="test_user"))
        b.save()
        # Recupera board, assert contenuto campi
        b = Board.objects.get(nome="test_board")
        self.assertEqual(b.nome, "test_board")
        self.assertEqual(len(b.utentiAssociati.all()), 1)
        self.assertEqual(b.utentiAssociati.all()[0].username, "test_user")

    def test_get_colonne(self):
        # Verifica metodo getColonneBoard()
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.getColonneBoard()), 2)
        self.assertEqual(b.getColonneBoard()[0].nome, "test_col1")

    def test_crea_colonna(self):
        # Verifica metodo creaColonna
        b = Board.objects.get(nome="test_board")
        b.creaColonna("test_col3")
        self.assertEqual(b.getColonneBoard()[2].nome, "test_col3")

    def test_modifica_colonna(self):
        # Verifica stato iniziale
        b = Board.objects.get(nome="test_board")
        self.assertEqual(b.getColonneBoard()[1].nome, "test_col2")
        b.modificaColonna("test_col2", "test_col_2")
        # Assert campi modificati
        self.assertEqual(b.getColonneBoard()[1].nome, "test_col_2")

    def test_muovi_card(self):
        # Verifica stato iniziale
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.getColonneBoard()[0].getCardColonna()), 1)
        self.assertEqual(len(b.getColonneBoard()[1].getCardColonna()), 0)
        self.assertEqual(b.getColonneBoard()[0].getCardColonna()[0].titolo, "test_card")
        b.muoviCard("test_col1", "test_col2", "test_card")
        # Assert nuovo stato
        self.assertEqual(len(b.getColonneBoard()[1].getCardColonna()), 1)
        self.assertEqual(len(b.getColonneBoard()[0].getCardColonna()), 0)
        self.assertEqual(b.getColonneBoard()[1].getCardColonna()[0].titolo, "test_card")

    def test_lista_utenti_associati(self):
        # Verifica stato iniziale
        b = Board.objects.get(nome="test_board")
        self.assertEqual(len(b.utentiAssociati.all()), 0)
        # Modifica stato
        b.utentiAssociati.add(ScrumUser.objects.get(username="test_user"))
        b.save()
        # Assert stato modificato
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
        # Verifica campi
        self.assertEqual(c.nome, "test_col1")
        self.assertEqual(c.boardParent.nome, "test_board")

    def test_get_card_colonna(self):
        c = Colonna.objects.get(nome="test_col1")
        # Verifica dati getCardColonna()
        self.assertEqual(len(c.getCardColonna()), 2)
        self.assertEqual(c.getCardColonna()[0].titolo, "test_card1")
        self.assertEqual(c.getCardColonna()[1].storyPoint, 3)

    def test_crea_card(self):
        c = Colonna.objects.get(nome="test_col1")
        # Stato iniziale
        self.assertEqual(len(c.getCardColonna()), 2)
        c.creaCard("test_card3", "test_desc", datetime.date.today(), 5, [])
        # Nuovo stato
        self.assertEqual(len(c.getCardColonna()), 3)
        self.assertEqual(c.getCardColonna()[2].titolo, "test_card3")

    def test_elimina_card(self):
        c = Colonna.objects.get(nome="test_col1")
        self.assertEqual(len(c.getCardColonna()), 2)
        c.eliminaCard("test_card2")
        # Assert nuovo stato
        self.assertEqual(len(c.getCardColonna()), 1)

    def test_modifica_card(self):
        c = Colonna.objects.get(nome="test_col1")
        # Stato iniziale
        self.assertEqual(c.getCardColonna()[0].titolo, "test_card1")
        self.assertEqual(c.getCardColonna()[0].descrizione, "test_desc")
        self.assertEqual(c.getCardColonna()[0].dataScadenza, datetime.date.today())
        self.assertEqual(c.getCardColonna()[0].storyPoint, 0)
        c.modificaCard("test_card1", "test_card_1", "test_desc_1", datetime.date(day=5, month=5, year=2020), 2)
        # Nuovo stato
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
        # Test campi statici della card
        self.assertEqual(c.titolo, "test_card2")
        self.assertEqual(c.descrizione, "test_desc")
        self.assertEqual(c.dataScadenza, datetime.date.today())
        self.assertEqual(c.storyPoint, 3)
        # Aggiunta utente associato
        c.utentiCard.add(ScrumUser.objects.get(username="test_user"))
        c.save()
        # Verifica ManyToMany
        c = Card.objects.get(titolo="test_card2")
        self.assertEqual(len(c.utentiCard.all()), 1)
        self.assertEqual(c.utentiCard.all()[0].username, "test_user")


# View Acceptance Test

class AcceptanceTestCase(TestCase):
    def setUp(self) -> None:
        # Crea utente + board + 2 colonne con 1 card ciascuna
        self.client.post('/register/',
                         {"username": "test_user", "password": "test_pass", "conferma_password": "test_pass"})
        self.client.post('/add_board/', {'nomeBoard': "test_board"})
        self.client.post('/add_column/', {'nomeColonna': 'test_col', 'boardParent': '0'})
        self.client.post('/add_column/', {'nomeColonna': 'test_col_other', 'boardParent': '0'})
        url = '/add_card/' + str(Board.objects.get(nome="test_board").id) + '/'
        self.client.post(url, {'nomeCard': "test_card", "descCard": "test_desc",
                                "dataCard": str(datetime.date.today()), "colonnaParent": '0'})
        self.client.post(url, {'nomeCard': "test_card_other", "descCard": "test_desc",
                               "dataCard": str(datetime.date.today()), "colonnaParent": '1'})
        self.client.logout()
        # Crea nuovo utente
        self.client.post('/register/',
                         {"username": "collab_user", "password": "collab_pass", "conferma_password": "collab_pass"})
        self.client.logout()

    def test_login_failure(self):
        # Se si cerca di fare login con credenziali sbagliate il login fallisce.
        response = self.client.post('/login/', {"username": "test_user", "password": "fail_pass"}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_ok(self):
        # Il login ha successo se si inseriscono i dati corretti.
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        response = self.client.post('/logout/', follow=True)
        #  Verifica stato non più loggato
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register(self):
        response = self.client.post('/register/', {"username": "test_user2", "password": "test_pass2", "conferma_password": "test_pass2"})
        # Verifica nuovo utente registrato con un login
        response = self.client.post('/login/', {"username": "test_user2", "password": "test_pass2"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_dashboard(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.get('/dashboard/')
        # Assert contenuto statico template
        self.assertContains(response, "Le tue Board")
        # Assert contenuto dinamico board
        self.assertContains(response, "test_board")

    def test_add_board(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.post('/add_board/', {'nomeBoard': "test_board2"})
        # Verifica aggiunta nuova board
        response = self.client.get('/dashboard/')
        self.assertContains(response, "test_board2")


    def test_add_column(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.post('/add_column/', {'nomeColonna': 'test_col2', 'boardParent': '0'})
        # Verifica l'esistenza della nuova board
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_col2")

    def test_add_card(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/add_card/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.post(url, {'nomeCard': "test_card1", "descCard": "test_desc",
                                          "dataCard": str(datetime.date.today()), "colonnaParent": '0'})
        # Conferma l'esistenza della nuova card
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_card1")

    def test_add_user(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/add_user/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.post(url, {"utentiRegistrati": '0'})
        response = self.client.get(url)
        # Collab_user non appare nella lista di utenti associabili
        self.assertNotContains(response, "<option value=\"0\">collab_user")
        response = self.client.post(url, {"utentiAssociati": '1'})
        response = self.client.get(url)
        # Collab_user appare nella lista di utenti associabili
        self.assertContains(response, "<option value=\"0\">collab_user")

    def test_edit_column_fields(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        # Test sulle funzionalità di modifyColumnForm
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col/'
        response = self.client.post(url, {"nomeColonna": 'test_col_1'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_col_1")
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        # Verifica nuovo stato dalla url di link.
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_1/test_card_other/">test_card_other</a>')
        self.assertContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                            + '/test_col_other/test_card_other/">test_card_other</a>')

    def test_edit_column_add_card(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        # AddCardToColForm
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col/'
        response = self.client.post(url, {"cardEsistenti": '0'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        # Verifica nuovo stato dalla url di link.
        self.assertContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                            + '/test_col/test_card_other/">test_card_other</a>')
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_other/test_card_other/">test_card_other</a>')
        # DeleteCardForm
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col/'
        response = self.client.post(url, {"cardAssociate": '1'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        # Verifica nuovo stato dalla url di link.
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col/test_card_other/">test_card_other</a>')
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_other/test_card_other/">test_card_other</a>')

    def test_edit_card_fields(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card/'
        # ModifyCardForm
        response = self.client.post(url, {"nomeCard": 'test_card_1', "descCard": "desc_card_1",
                                          "dataCard": datetime.date.today(), "colonnaParent": "0", "storyPoint": "5"})

        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card_1/'
        response = self.client.get(url)
        # Verifica nuovo stato
        self.assertContains(response, "test_card_1")
        self.assertContains(response, "name=\"storyPoint\" value=\"5\"")

    def test_edit_card_add_user(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        # addUserForm
        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card/'
        response = self.client.post(url, {"utentiRegistrati": '0'})
        response = self.client.get(url)
        # Collab_user non appare nella lista di utenti associabili
        self.assertNotContains(response, "<option value=\"0\">collab_user")
        # delUserForm
        response = self.client.post(url, {"utentiAssociati": '1'})
        response = self.client.get(url)
        # Collab_user appare nella lista di utenti associabili
        self.assertContains(response, "<option value=\"0\">collab_user")

    def test_board_details(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        # Verifica elementi statici e dinamici
        self.assertContains(response, "test_board")
        self.assertContains(response, "test_col")
        self.assertContains(response, "test_card")
        self.assertContains(response, "test_col_other")
        self.assertContains(response, "test_card_other")
        self.assertContains(response, "Aggiungi Utente</button>")

    def test_burndown(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/burndown/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        # Verifica dei valori previsti e della struttura della pagina
        self.assertContains(response, "test_col: 1")
        self.assertContains(response, "test_col_other: 1")
        self.assertNotContains(response, "test_col_other: 2")
        self.assertContains(response,
                            "Numero di Card della Board:</th>\n                    <td>\n                        <p>2")
        self.assertContains(response,
                            "Numero di Card Scadute:</th>\n                    <td>\n                        <p>0")
        self.assertContains(response,
                            "Numero di Punti Storia Utilizzati:</th>\n                    <td>\n                        <p>0")
