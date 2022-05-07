import pytest


@pytest.fixture
def default_icons(db):
    from finance.models import Icon
    Icon.create_defaults()


@pytest.fixture
def user(default_icons, django_user_model):
    return django_user_model.objects.create(
        username="test",
        email="test.test@test.com",
    )
