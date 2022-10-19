"""Watcher's middlewares"""
import random

from django.conf import settings
from django.urls import Resolver404, resolve
from django.utils import timezone

from .models import Request


class StatisticsStartMiddleware:  # pylint: disable=too-few-public-methods
    """Start time at request coming in"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        "Start time at request coming in"
        request.start_time = timezone.now()
        response = self.get_response(request)
        return response


class StatisticsFinishMiddleware:  # pylint: disable=too-few-public-methods
    """Store request in DB"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        "End of request, take time"
        if _allow_request(rate=settings.WATCHER_REQUEST_RATE):
            _store_request(request)
        response = self.get_response(request)
        return response


def _allow_request(rate):
    """Check if request is allowed to be stored based on rate limit"""
    return random.randint(1, 100) <= rate


def _store_request(request):
    """Store request in DB"""
    try:
        resolver_match = resolve(request.path_info)
    except Resolver404:
        resolver_match = None
    Request.objects.create(
        started_at=request.start_time,
        duration=timezone.now() - request.start_time,
        method=request.method,
        path=request.path,
        route=resolver_match.route if resolver_match else None,
        url_name=resolver_match.url_name if resolver_match else None,
        app_name=resolver_match.app_name if resolver_match else "",
        user=request.user if request.user.is_authenticated else None,
    )
