"""Global config for pytest"""
import pytest


@pytest.fixture
def default_icons():
    """Create default icons"""
    from finance.models import Icon  # pylint: disable=import-outside-toplevel

    Icon.create_defaults()


@pytest.fixture
@pytest.mark.usefixtures("default_icons")
def user(django_user_model):
    """A sample user"""
    return django_user_model.objects.create(
        username="test",
        email="test.test@test.com",
    )
