import pytest
from django.test import Client
from django.utils.timezone import now
from finance.models import Icon

from .models import Configuration, Snippet, Tag


@pytest.mark.django_db
class TestChecklists:

    @pytest.fixture
    def default_icons(self):
        Icon.create_defaults()

    @pytest.fixture
    def user(self, django_user_model, default_icons):
        return django_user_model.objects.create(username='test', email='test.test@test.com')

    @pytest.fixture
    def another_user(self, django_user_model, default_icons):
        return django_user_model.objects.create(username='anothertest', email='another.test@test.com')

    def test_root(self, client: Client, user):
        Snippet.objects.create(title='test', code='print("hello world")', created_by=user)
        client.force_login(user)
        response = client.get('/cd/')
        assert response.status_code == 200

    def test_list_snippets(self, client: Client, user):
        snippet: Snippet = Snippet.objects.create(title='test', code='print("hello world")', created_by=user)
        client.force_login(user)
        response = client.get('/cd/api/snippets/')
        assert response.status_code == 200
        assert response.json()['results'][0] == {
            'id': snippet.id,
            'title': snippet.title,
            'code': snippet.code,
            'language': snippet.language,
            'html': snippet.html,
            'public': snippet.public,
            'public_id': str(snippet.public_id),
            'tags': [],
        }
