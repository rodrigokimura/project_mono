import hashlib
import json
import logging
from datetime import datetime
from logging import LogRecord
from types import TracebackType

from django.http import HttpRequest


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class WatcherHandler(logging.Handler):
    """An exception log handler that stores log entries to database.
    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    """

    def emit(self, record: LogRecord):
        try:
            self.store_log(record)
        except Exception:
            pass
        # print(record.name)
        # print(record.levelname)
        # print(record.created)
        # print(record.pathname)
        # print(record.lineno)
        # print(record.status_code)
        # print(record.exc_info)
        # print(record.exc_text)
        # print(record.thread)
        # print(record.threadName)

    def store_log(self, record: LogRecord):
        from watcher.models import Event, Issue, Traceback
        try:
            request: HttpRequest = record.request
            user = record.request.user
        except Exception:
            request = None
            user = None
        if record.exc_info is not None:
            issue, created = Issue.objects.update_or_create(
                hash=hashlib.sha256(
                    bytes(record.exc_text, encoding='utf-8')
                ).hexdigest(),
                defaults={
                    'name': record.exc_info[0].__name__,
                    'description': str(record.exc_info[1]),
                }
            )
            if created:
                tb: TracebackType = record.exc_info[2]
                order = 1
                while tb.tb_next is not None:
                    fr = tb.tb_frame
                    variables = {k: v if is_jsonable(v) else repr(v) for k, v in fr.f_locals.items()}
                    code_text = self.get_code_text(
                        fr.f_code.co_filename,
                        tb.tb_lineno
                    )
                    Traceback.objects.create(
                        issue=issue,
                        order=order,
                        file_name=fr.f_code.co_filename,
                        function_name=fr.f_code.co_name,
                        line_number=tb.tb_lineno,
                        code_text=code_text,
                        variables=variables,
                    )
                    tb = tb.tb_next
                    order += 1
            Event.objects.create(
                issue=issue,
                timestamp=datetime.fromtimestamp(record.created),
                user=user,
            )

    def get_code_text(self, file_name, line_number):
        code_file = open(file_name, 'r')
        content = code_file.readlines()
        # code = [(i + 1, content[i]) for i in range(l - 7, l + 6)]
        # ''.join(content[l - 7:l + 6])
        if line_number >= 7:
            start = 0
        else:
            start = line_number - 7
        if len(content) >= line_number + 6:
            end = line_number + 6
        else:
            end = len(content) - 1
        return content[start: end]
