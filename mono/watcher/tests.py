import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from .models import Issue


@pytest.mark.django_db
class TestWatcherViews:

    @pytest.fixture
    def issue(self):
        return Issue.objects.create(
            hash=str(uuid.uuid4()),
            name='fake issue',
            description='Just a fake issue'
        )

    def test_mark_issue_as_resolved_should_succeed(self, issue, admin_client):
        response = admin_client.post(
            reverse('watcher:issue_resolve', args=[issue.id]),
            {'resolved': True},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'success': True}
        assert issue.resolved_at is not None

    def test_mark_issue_as_resolved_with_invalid_payload_should_fail(self, issue, admin_client):
        response = admin_client.post(
            reverse('watcher:issue_resolve', args=[issue.id]),
            {'resolved': 'resolved'},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'resolved': ['Must be a valid boolean.']}
        assert issue.resolved_at is None

    def test_mark_issue_as_unresolved_should_succeed(self, issue, admin_client, admin_user):
        issue.resolve(admin_user)
        response = admin_client.post(
            reverse('watcher:issue_resolve', args=[issue.id]),
            {'resolved': False},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'success': True}
        assert issue.resolved_at is None

    def test_mark_issue_as_ignored_should_succeed(self, issue, admin_client):
        response = admin_client.post(
            reverse('watcher:issue_ignore', args=[issue.id]),
            {'ignored': True},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'success': True}
        assert issue.ignored_at is not None

    def test_mark_issue_as_ignored_with_invalid_payload_should_fail(self, issue, admin_client):
        response = admin_client.post(
            reverse('watcher:issue_ignore', args=[issue.id]),
            {'ignored': 'ignored'},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'ignored': ['Must be a valid boolean.']}
        assert issue.ignored_at is None

    def test_mark_issue_as_not_ignored_should_succeed(self, issue, admin_client, admin_user):
        issue.ignore(admin_user)
        response = admin_client.post(
            reverse('watcher:issue_ignore', args=[issue.id]),
            {'ignored': False},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'success': True}
        assert issue.ignored_at is None
