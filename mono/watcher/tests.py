import textwrap
import uuid
from logging import LogRecord
from unittest.mock import mock_open, patch

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects
from rest_framework import status
from watcher.log_handlers import (
    WatcherHandler,
    get_code_text,
    handle_traceback,
    is_jsonable,
    store_log,
)

from .models import Event, Issue, Traceback


class FakeCode(object):
    def __init__(self, co_filename, co_name):
        self.co_filename = co_filename
        self.co_name = co_name


class FakeFrame(object):
    def __init__(self, f_code, f_globals, f_locals):
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals


class FakeTraceback(object):
    def __init__(self, frames, line_nums):
        if len(frames) != len(line_nums):
            raise ValueError("Ya messed up!")
        self._frames = frames
        self._line_nums = line_nums
        self.tb_frame = frames[0]
        self.tb_lineno = line_nums[0]

    @property
    def tb_next(self):
        if len(self._frames) > 1:
            return FakeTraceback(self._frames[1:], self._line_nums[1:])


class FakeException(Exception):
    def __init__(self, *args, **kwargs):
        self._tb = None
        super().__init__(*args, **kwargs)

    @property
    def __traceback__(self):
        return self._tb

    @__traceback__.setter
    def __traceback__(self, value):
        self._tb = value

    def with_traceback(self, value):
        self._tb = value
        return self


@pytest.mark.django_db
class TestWatcherViews:
    @pytest.fixture
    def issue(self):
        return Issue.objects.create(
            hash=str(uuid.uuid4()),
            name="fake issue",
            description="Just a fake issue",
        )

    @pytest.fixture
    def code_file(self):
        return textwrap.dedent(
            """
            def hello_world():
                print("hello world")
            
            def sum_a_b(a, b):
                return a + b
            
            assert sum_a_b(1, 2) == 3
            assert sum_a_b(4, 5) == 9
        """
        )

    @pytest.fixture
    def fake_exception(self):
        code1 = FakeCode("made_up_filename.py", "non_existent_function")
        code2 = FakeCode(
            "another_non_existent_file.py", "another_non_existent_method"
        )
        frame1 = FakeFrame(code1, {}, {})
        frame2 = FakeFrame(code2, {}, {})
        tb = FakeTraceback([frame1, frame2], [1, 3])
        exc = FakeException("yo").with_traceback(tb)
        return exc

    @pytest.fixture
    def log_record(self, fake_exception: FakeException):
        return LogRecord(
            name="mock",
            level=1,
            pathname="pathname",
            lineno=1,
            msg="msg",
            args=None,
            exc_info=(
                FakeException,
                fake_exception,
                fake_exception.__traceback__,
            ),
            func=None,
            sinfo="sinfo",
        )

    def test_root_with_superuser_should_succeed(self, admin_client: Client):
        response = admin_client.get(
            reverse("watcher:index"),
        )
        assert response.status_code == status.HTTP_200_OK

    def test_root_with_non_superuser_should_fail(self, issue, client: Client):
        response = client.get(reverse("watcher:index"))
        assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('watcher:index')}",
        )

    def test_issue_detail_with_superuser_should_succeed(
        self, issue: Issue, admin_client: Client
    ):
        response = admin_client.get(
            reverse("watcher:issue_detail", args=[issue.id]),
        )
        assertContains(response, issue)
        assert response.status_code == status.HTTP_200_OK

    def test_issue_detail_with_non_superuser_should_fail(
        self, issue: Issue, client: Client
    ):
        response = client.get(
            reverse("watcher:issue_detail", args=[issue.id]),
        )
        assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('watcher:issue_detail', args=[issue.id])}",
        )

    def test_mark_issue_as_resolved_should_succeed(
        self, issue: Issue, admin_client: Client
    ):
        response = admin_client.post(
            reverse("watcher:issue_resolve", args=[issue.id]),
            {"resolved": True},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"success": True}
        assert issue.resolved_at is not None

    def test_mark_issue_as_resolved_with_invalid_payload_should_fail(
        self, issue: Issue, admin_client: Client
    ):
        response = admin_client.post(
            reverse("watcher:issue_resolve", args=[issue.id]),
            {"resolved": "resolved"},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"resolved": ["Must be a valid boolean."]}
        assert issue.resolved_at is None

    def test_mark_issue_as_unresolved_should_succeed(
        self, issue: Issue, admin_client: Client, admin_user
    ):
        issue.resolve(admin_user)
        response = admin_client.post(
            reverse("watcher:issue_resolve", args=[issue.id]),
            {"resolved": False},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"success": True}
        assert issue.resolved_at is None

    def test_mark_issue_as_ignored_should_succeed(
        self, issue: Issue, admin_client: Client
    ):
        response = admin_client.post(
            reverse("watcher:issue_ignore", args=[issue.id]),
            {"ignored": True},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"success": True}
        assert issue.ignored_at is not None

    def test_mark_issue_as_ignored_with_invalid_payload_should_fail(
        self, issue: Issue, admin_client: Client
    ):
        response = admin_client.post(
            reverse("watcher:issue_ignore", args=[issue.id]),
            {"ignored": "ignored"},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"ignored": ["Must be a valid boolean."]}
        assert issue.ignored_at is None

    def test_mark_issue_as_not_ignored_should_succeed(
        self, issue: Issue, admin_client: Client, admin_user
    ):
        issue.ignore(admin_user)
        response = admin_client.post(
            reverse("watcher:issue_ignore", args=[issue.id]),
            {"ignored": False},
        )
        issue.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"success": True}
        assert issue.ignored_at is None

    def test_is_jsonable(self):
        assert is_jsonable(".1")
        assert is_jsonable({"a": 1})
        assert is_jsonable(0.1)
        assert is_jsonable(lambda: True) is False

    def test_get_code_text(self, code_file):
        with patch(
            "builtins.open", mock_open(read_data=code_file)
        ) as mock_file:
            result = get_code_text("path", 1)
            assert list(result)[1] == (2, "def hello_world():\n")
            result = get_code_text("path", 7)
            assert list(result)[1] == (2, "def hello_world():\n")

    def test_handle_traceback(
        self, fake_exception: FakeException, issue: Issue, code_file
    ):
        watcher_tracebacks = Traceback.objects.all()
        assert watcher_tracebacks.exists() is False
        with patch(
            "builtins.open", mock_open(read_data=code_file)
        ) as mock_file:
            handle_traceback(fake_exception.__traceback__, issue)
        assert watcher_tracebacks.all().exists()
        assert watcher_tracebacks.count() == 2

    def test_log_handler(
        self,
        fake_exception: FakeException,
        issue: Issue,
        code_file,
        log_record: LogRecord,
    ):
        log_record.exc_text = "123"
        watcher_tracebacks = Traceback.objects.all()
        watcher_events = Event.objects.all()
        assert watcher_tracebacks.exists() is False
        assert watcher_events.exists() is False
        with patch(
            "builtins.open", mock_open(read_data=code_file)
        ) as mock_file:
            WatcherHandler().emit(log_record)
            store_log(log_record)
        assert watcher_tracebacks.count() == 2
        assert watcher_events.count() == 2

    def test_log_handler_on_exception_should_do_nothing(
        self,
        fake_exception: FakeException,
        issue: Issue,
        code_file,
        log_record: LogRecord,
    ):
        log_record.exc_text = "123"
        watcher_tracebacks = Traceback.objects.all()
        watcher_events = Event.objects.all()
        assert watcher_tracebacks.exists() is False
        with patch(
            "builtins.open",
            mock_open(read_data=code_file),
        ), patch(
            "watcher.log_handlers.store_log",
            lambda rec: rec,
        ) as mock_file:
            mock_file.side_effect = Exception("fake exception")
            WatcherHandler().emit(log_record)
        assert watcher_tracebacks.exists() is False
        assert watcher_events.exists() is False
