"""Log handlers used by Watcher"""
import hashlib
import json
import logging
from datetime import datetime
from logging import LogRecord
from types import TracebackType

import pytz
from django.http import HttpRequest


def is_jsonable(var):
    """
    Check if var is JSON serializable
    """
    try:
        json.dumps(var)
        return True
    except (TypeError, OverflowError):
        return False


def get_code_text(file_name, line_number):
    """
    Get code block text around a given line number
    """
    with open(file_name, encoding='utf-8', mode='r') as code_file:
        content = code_file.readlines()
    if line_number < 7:
        start = 0
    else:
        start = line_number - 7
    if len(content) >= line_number + 6:
        end = line_number + 6
    else:
        end = len(content)
    return zip(range(start + 1, end + 2), content[start: end])


def handle_traceback(traceback: TracebackType, issue):
    """
    Create traceback model instance from python's traceback
    """
    from watcher.models import \
        Traceback  # pylint: disable=import-outside-toplevel
    order = 1
    while traceback is not None:
        frame = traceback.tb_frame
        variables = {
            k: v if is_jsonable(v) else repr(v)
            for k, v in frame.f_locals.items()
        }
        code_text = get_code_text(
            frame.f_code.co_filename,
            traceback.tb_lineno
        )
        Traceback.objects.create(
            issue=issue,
            order=order,
            file_name=frame.f_code.co_filename,
            function_name=frame.f_code.co_name,
            line_number=traceback.tb_lineno,
            code_text={k: v.rstrip('\n') for k, v in code_text},
            variables=variables,
        )
        traceback = traceback.tb_next
        order += 1


def store_log(record: LogRecord):
    """
    Store log record
    """
    from watcher.models import (  # pylint: disable=import-outside-toplevel
        Event, Issue,
    )
    try:
        request: HttpRequest = record.request
        user = request.user if request.user.is_authenticated else None
    except Exception:  # pylint: disable=broad-except
        request = None
        user = None
    if record.exc_info is None:
        return
    issue, created = Issue.objects.update_or_create(
        hash=hashlib.sha256(
            record.exc_text.encode('utf-8')
        ).hexdigest(),
        defaults={
            'name': record.exc_info[0].__name__,
            'description': str(record.exc_info[1]),
        }
    )
    if created:
        traceback: TracebackType = record.exc_info[2]
        handle_traceback(traceback, issue)
    Event.objects.create(
        issue=issue,
        timestamp=datetime.fromtimestamp(
            record.created,
            tz=pytz.UTC
        ),
        user=user,
    )


class WatcherHandler(logging.Handler):
    """An exception log handler that stores log entries to database.
    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    """

    def emit(self, record: LogRecord):
        try:
            store_log(record)
        except Exception:  # pylint: disable=broad-except
            pass
