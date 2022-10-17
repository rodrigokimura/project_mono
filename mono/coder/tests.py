import pytest
from django.test import Client
from finance.models import Icon

from .models import Snippet, Tag


@pytest.mark.django_db
class TestCoder:
    @pytest.fixture
    def default_icons(self):
        Icon.create_defaults()

    @pytest.fixture
    def user(self, django_user_model, default_icons):
        return django_user_model.objects.create(
            username="test", email="test.test@test.com"
        )

    @pytest.fixture
    def sample_snippet(self, user):
        return Snippet.objects.create(
            title="test", code='print("hello world")', created_by=user
        )

    @pytest.fixture
    def sample_tag(self, user):
        return Tag.objects.create(name="hello_world", created_by=user)

    @pytest.fixture
    def sample_snippets(self, user, sample_tag: Tag):
        Snippet.objects.create(
            title="test1",
            code='print("hello world")',
            created_by=user,
        ).tags.add(sample_tag)
        Snippet.objects.create(
            title="test2", code='print("hello world")', created_by=user
        ).tags.add(sample_tag)
        Snippet.objects.create(
            title="test3",
            code='console.log("hello world")',
            created_by=user,
            language="javascript",
        ).tags.add(sample_tag)
        Snippet.objects.create(
            title="test4",
            code="list(filter(None, lst))",
            created_by=user,
            language="python",
        )

    def test_root(self, client: Client, user, sample_snippet: Snippet):
        client.force_login(user)
        response = client.get("/cd/")
        assert response.status_code == 200

    def test_list_snippets(self, client: Client, user, sample_snippet: Snippet):
        client.force_login(user)
        response = client.get("/cd/api/snippets/")
        assert response.status_code == 200
        assert response.json()["results"][0] == {
            "id": sample_snippet.id,
            "title": sample_snippet.title,
            "code": sample_snippet.code,
            "language": sample_snippet.language,
            "html": sample_snippet.html,
            "public": sample_snippet.public,
            "public_id": str(sample_snippet.public_id),
            "tags": [],
        }

    def test_list_languages(self, client: Client, user, sample_snippets):
        client.force_login(user)
        response = client.get("/cd/api/snippets/languages/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "language": "python",
                "count": 3,
            },
            {
                "language": "javascript",
                "count": 1,
            },
        ]

    def test_list_tags(self, client: Client, user, sample_snippets, sample_tag):
        client.force_login(user)
        response = client.get("/cd/api/snippets/tags/")
        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "name": "hello_world", "color": "blue", "count": 3},
            {"id": None, "name": None, "count": 1},
        ]

    def test_tag(self, client: Client, user, sample_snippets, sample_tag: Tag):
        untagged_snippet: Snippet = Snippet.objects.get(title="test4")
        assert untagged_snippet.tags.exists() is False
        client.force_login(user)
        response = client.post(
            f"/cd/api/snippets/{untagged_snippet.pk}/tag/",
            data={"tag": sample_tag.pk},
        )
        assert response.status_code == 204
        untagged_snippet.refresh_from_db()
        assert untagged_snippet.tags.count() == 1
        assert untagged_snippet.tags.first() == sample_tag

    def test_untag(
        self, client: Client, user, sample_snippets, sample_tag: Tag
    ):
        tagged_snippet: Snippet = Snippet.objects.get(title="test1")
        assert tagged_snippet.tags.count() == 1
        assert tagged_snippet.tags.first() == sample_tag
        client.force_login(user)
        response = client.post(
            f"/cd/api/snippets/{tagged_snippet.pk}/untag/",
            data={"tag": sample_tag.pk},
        )
        assert response.status_code == 204
        tagged_snippet.refresh_from_db()
        assert tagged_snippet.tags.exists() is False
