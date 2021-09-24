from django.test import TestCase

from .models import Module


class ModelTests(TestCase):
    def test_module(self):
        module = Module.objects.create(name='test')
        self.assertEqual(str(module), 'test')
