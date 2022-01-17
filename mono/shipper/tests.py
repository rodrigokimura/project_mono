from django.test import TestCase

from .models import Ship


class ViewTests(TestCase):

    def test_root(self):
        response = self.client.get('/shipper/')
        self.assertEqual(response.status_code, 200)

    def test_create_view_get(self):
        response = self.client.get('/shipper/ships/')
        self.assertEqual(response.status_code, 200)

    def test_create_view_post(self):
        response = self.client.post('/shipper/ships/', data={'name_1': 'teste', 'name_2': 'aleatorio'})
        self.assertEqual(response.status_code, 302)


class ModelTests(TestCase):

    def test_ship_str(self):
        ship: Ship = Ship.objects.create(name_1='teste', name_2='aleatorio')
        self.assertEqual(str(ship), 'teste + aleatorio')

    def test_portmanteaus(self):
        ship: Ship = Ship.objects.create(name_1='teste', name_2='aleatorio')
        portmanteaus = [str(p) for p in ship.portmanteaus.all()]
        self.assertIn('teleatorio', portmanteaus)
        self.assertIn('aste', portmanteaus)
        self.assertIn('tetorio', portmanteaus)
        self.assertIn('aleaste', portmanteaus)
        self.assertIn('terio', portmanteaus)
        self.assertIn('aleatoste', portmanteaus)
