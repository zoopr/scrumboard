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
        self.client.post('/add_column/', {'nomeColonna': 'test_col_other', 'boardParent': '0'})
        url = '/add_card/' + str(Board.objects.get(nome="test_board").id) + '/'
        self.client.post(url, {'nomeCard': "test_card", "descCard": "test_desc",
                                "dataCard": str(datetime.date.today()), "colonnaParent": '0'})
        self.client.post(url, {'nomeCard': "test_card_other", "descCard": "test_desc",
                               "dataCard": str(datetime.date.today()), "colonnaParent": '1'})
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
        response = self.client.post('/logout/', follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register(self):
        response = self.client.post('/register/', {"username": "test_user2", "password": "test_pass2", "conferma_password": "test_pass2"})
        response = self.client.post('/login/', {"username": "test_user2", "password": "test_pass2"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_dashboard(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.get('/dashboard/')
        self.assertContains(response, "Le tue Board")
        self.assertContains(response, "test_board")

    def test_add_board(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.post('/add_board/', {'nomeBoard': "test_board2"})
        response = self.client.get('/dashboard/')
        self.assertContains(response, "test_board2")

    def test_add_column(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        response = self.client.post('/add_column/', {'nomeColonna': 'test_col2', 'boardParent': '0'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_col2")

    def test_add_card(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/add_card/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.post(url, {'nomeCard': "test_card1", "descCard": "test_desc",
                                          "dataCard": str(datetime.date.today()), "colonnaParent": '0'})
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

    def test_edit_column(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        # modifyColumnForm
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col/'
        response = self.client.post(url, {"nomeColonna": 'test_col_1'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, "test_col_1")
        # AddCardToColForm
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_1/test_card_other/">test_card_other</a>')
        self.assertContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                            + '/test_col_other/test_card_other/">test_card_other</a>')
        #
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col_1/'
        response = self.client.post(url, {"cardEsistenti": '0'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                            + '/test_col_1/test_card_other/">test_card_other</a>')
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_other/test_card_other/">test_card_other</a>')
        # DeleteCardForm
        url = '/edit_column/' + str(Board.objects.get(nome="test_board").id) + '/test_col_1/'
        response = self.client.post(url, {"cardAssociate": '1'})
        url = '/board/' + str(Board.objects.get(nome="test_board").id) + '/'
        response = self.client.get(url)
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_1/test_card_other/">test_card_other</a>')
        self.assertNotContains(response, '<a href="/edit_card/' + str(Board.objects.get(nome="test_board").id)
                               + '/test_col_other/test_card_other/">test_card_other</a>')

    def test_edit_card(self):
        response = self.client.post('/login/', {"username": "test_user", "password": "test_pass"})
        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card/'
        # ModifyCardForm
        response = self.client.post(url, {"nomeCard": 'test_card_1', "descCard": "desc_card_1",
                                          "dataCard": datetime.date.today(), "colonnaParent": "0", "storyPoint": "5"})

        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card_1/'
        response = self.client.get(url)
        self.assertContains(response, "test_card_1")
        self.assertContains(response, "name=\"storyPoint\" value=\"5\"")
        # addUserForm
        url = '/edit_card/' + str(Board.objects.get(nome="test_board").id) + '/test_col/test_card_1/'
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
        self.assertContains(response, "test_col: 1")
        self.assertContains(response, "test_col_other: 1")
        self.assertNotContains(response, "test_col_other: 2")
        self.assertContains(response,
                            "Numero di Card della Board:</th>\n                    <td>\n                        <p>2")
        self.assertContains(response,
                            "Numero di Card Scadute:</th>\n                    <td>\n                        <p>0")
        self.assertContains(response,
                            "Numero di Punti Storia Utilizzati:</th>\n                    <td>\n                        <p>0")
