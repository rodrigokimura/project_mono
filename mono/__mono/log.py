import logging
from http import HTTPStatus

import sqlparse
from __mono.constants import HTTPMethod
from colorama.ansi import Back, Fore, Style


def pretty_sql(statement):
    return sqlparse.format(statement, reindent=True, keyword_case="upper")


class HttpStatusStyle:
    @classmethod
    def format(cls, status_code, prefix):
        return f"{prefix} {status_code} {Style.BRIGHT}{HTTPStatus(status_code).phrase} {Style.RESET_ALL}"

    @classmethod
    def HTTP_SUCCESS(cls, status_code):
        return cls.format(status_code, Back.GREEN)

    @classmethod
    def HTTP_INFO(cls, status_code):
        return cls.format(status_code, Back.WHITE)

    @classmethod
    def HTTP_NOT_MODIFIED(cls, status_code):
        return cls.format(status_code, Back.CYAN)

    @classmethod
    def HTTP_REDIRECT(cls, status_code):
        return cls.format(status_code, Back.CYAN)

    @classmethod
    def HTTP_NOT_FOUND(cls, status_code):
        return cls.format(status_code, Back.YELLOW)

    @classmethod
    def HTTP_BAD_REQUEST(cls, status_code):
        return cls.format(status_code, Back.LIGHTRED_EX)

    @classmethod
    def HTTP_SERVER_ERROR(cls, status_code):
        return cls.format(status_code, Back.RED)


class HttpMethodStyle:
    @classmethod
    def format(cls, method, url, prefix):
        return f"{Style.BRIGHT}{prefix}{method}{Style.NORMAL} {url}{Style.RESET_ALL}"

    @classmethod
    def read(cls, method, url):
        return cls.format(method, url, Fore.BLUE)

    @classmethod
    def edit(cls, method, url):
        return cls.format(method, url, Fore.YELLOW)

    @classmethod
    def delete(cls, method, url):
        return cls.format(method, url, Fore.RED)

    @classmethod
    def other(cls, method, url):
        return cls.format(method, url, Fore.GREEN)


class CustomServerFormatter(logging.Formatter):
    default_time_format = "%d/%b/%Y %H:%M:%S"

    def __init__(self, *args, **kwargs):
        self.status_style = HttpStatusStyle
        self.method_style = HttpMethodStyle
        super().__init__(*args, **kwargs)

    def format(self, record):

        method, url, protocol = record.args[0].split()

        endpoint = f"{method} {url}"

        status_code = getattr(record, "status_code", None)

        if status_code:
            if 200 <= status_code < 300:
                # Put 2XX first, since it should be the common case
                status_code = self.status_style.HTTP_SUCCESS(status_code)
            elif 100 <= status_code < 200:
                status_code = self.status_style.HTTP_INFO(status_code)
            elif status_code == 304:
                status_code = self.status_style.HTTP_NOT_MODIFIED(status_code)
            elif 300 <= status_code < 400:
                status_code = self.status_style.HTTP_REDIRECT(status_code)
            elif status_code == 404:
                status_code = self.status_style.HTTP_NOT_FOUND(status_code)
            elif 400 <= status_code < 500:
                status_code = self.status_style.HTTP_BAD_REQUEST(status_code)
            else:
                # Any 5XX, or any other status code
                status_code = self.status_style.HTTP_SERVER_ERROR(status_code)

        if method == HTTPMethod.GET:
            endpoint = self.method_style.read(method, url)
        elif method in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
            endpoint = self.method_style.edit(method, url)
        elif method == HTTPMethod.DELETE:
            endpoint = self.method_style.delete(method, url)
        else:
            endpoint = self.method_style.other(method, url)

        if self.uses_server_time() and not hasattr(record, "server_time"):
            record.server_time = self.formatTime(record, self.datefmt)

        record.msg = "%(endpoint)s %(status_code)s"
        record.args = {"endpoint": endpoint, "status_code": status_code}

        formatter = logging.Formatter(
            f"{Style.DIM}%(asctime)s {Style.BRIGHT}[SERVER]{Style.RESET_ALL} %(message)s"
        )
        return formatter.format(record)

    def uses_server_time(self):
        return self._fmt.find("{server_time}") >= 0


class CustomDatabaseFormatter(logging.Formatter):
    def format(self, record):
        duration = record.args[0]
        sql = pretty_sql(record.args[1])

        record.msg = (
            f"\n{Fore.CYAN}%(sql)s\n{Style.DIM}%(duration)s{Style.RESET_ALL}"
        )
        record.args = {"sql": sql, "duration": duration}

        formatter = logging.Formatter(
            f"{Style.DIM}%(asctime)s {Style.BRIGHT}[DATABASE]{Style.RESET_ALL} %(message)s"
        )
        return formatter.format(record)
