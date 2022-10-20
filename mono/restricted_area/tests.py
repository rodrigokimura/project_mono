import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertContains

User = get_user_model()


@pytest.mark.django_db
class TestRestrictedAreaViews:
    def test_login_as_view(self, admin_client: Client, admin_user):
        response = admin_client.post(
            reverse("restricted-area:login_as"), {"user": admin_user.id}
        )
        assertContains(
            response, f"Successfully logged in as {admin_user.username}"
        )

    def test_force_error_500_should_raise_exception(
        self, admin_client: Client, admin_user
    ):
        with pytest.raises(Exception):
            response = admin_client.get(
                reverse("restricted-area:force-error-500")
            )
            assert response.status_code == 500
