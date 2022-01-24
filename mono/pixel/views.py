"""Pixel's views"""
import logging
from abc import abstractmethod
from base64 import b64decode
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pytz
from __mono.mixins import PassRequestToFormViewMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDay
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import SiteForm
from .models import Ping, Site


def get_timestamp(query_dict):
    """Get formatted timestamp from query_dict"""
    if 'ts' not in query_dict:
        return None
    epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
    milliseconds = int(query_dict.get('ts'))
    return epoch + timedelta(milliseconds=milliseconds)


def get_implicit_domain_name_url(full_url):
    """
        Convert full absolute URL to implicit domain name
        Eg:
            https://developer.mozilla.org/en-US/docs/Learn -> /en-US/docs/Learn
    """
    parsed_uri = urlparse(full_url)
    return parsed_uri.netloc


def shorten_url(full_url: str, site_id: str):
    """Convert to relative url is from same site"""
    qs = Site.objects.filter(id=site_id)
    if not qs.exists():
        return full_url

    site: Site = qs.first()
    parsed_uri = urlparse(full_url)
    if site.host in parsed_uri.netloc:
        return full_url.replace(
            f'{parsed_uri.scheme}://{parsed_uri.netloc}',
            ''
        )
    return full_url


def get_tracking_info(query_dict):
    """Parse data from query_dict"""
    site_id = query_dict.get('id').replace('ID-', '')
    tracking_info = {
        'site_id': site_id,
        'user_id': query_dict.get('uid'),
        'event': query_dict.get('ev'),
        'event_data': query_dict.get('ed'),
        'openpixel_js_version': query_dict.get('v'),
        'document_location': shorten_url(query_dict.get('dl'), site_id),
        'referrer_location': shorten_url(query_dict.get('rl'), site_id),
        'timestamp': get_timestamp(query_dict),
        'encoding': query_dict.get('de'),
        'screen_resolution': query_dict.get('sr'),
        'viewport': query_dict.get('vp'),
        'document_title': query_dict.get('dt'),
        'browser_name': query_dict.get('bn'),
        'mobile_device': query_dict.get('md', '').lower() == 'true',
        'user_agent': query_dict.get('ua'),
        'timezone_offset': int(query_dict.get('tz', None)),
        'utm_source': query_dict.get('utm_source'),
        'utm_medium': query_dict.get('utm_medium'),
        'utm_term': query_dict.get('utm_term'),
        'utm_content': query_dict.get('utm_content'),
        'utm_campaign': query_dict.get('utm_campaign'),
    }
    return tracking_info


def store_tracking_info(tracking_info):
    """Create ping instance"""
    if not Site.objects.filter(id=tracking_info.get('site_id')).exists():
        logging.warning('Invalid ping')
        return
    event = tracking_info['event']
    if event == 'pageclose':
        ping: Ping = Ping.objects.filter(
            site_id=tracking_info['site_id'],
            user_id=tracking_info['user_id'],
            document_location=tracking_info['document_location'],
        ).last()
        if ping is not None and ping.pageload_timestamp is not None:
            ping.pageclose_timestamp = tracking_info['timestamp']
            ping.duration = tracking_info['timestamp'] - ping.pageload_timestamp
            ping.save()
    if tracking_info['event'] == 'pageload':
        tracking_info['pageload_timestamp'] = tracking_info['timestamp']
    ping = Ping.objects.create(**tracking_info)


@csrf_exempt
def pixel_gif(request):
    """Pixel view that tracks data"""
    if request.GET:
        tracking_info = get_tracking_info(request.GET)
        store_tracking_info(tracking_info)
    return HttpResponse(
        b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"),
        content_type='image/gif'
    )


class RootView(LoginRequiredMixin, RedirectView):
    """Root view"""
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """Redirect to list of tags"""
        if not self.request.user.is_authenticated:
            # TODO: redirect to an informational page
            return None
        return reverse('pixel:tags')


class SiteCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, CreateView):
    """Register a new site"""
    model = Site
    form_class = SiteForm
    success_url = reverse_lazy('pixel:tags')


class SitesView(LoginRequiredMixin, ListView):
    """Display all registered sites"""

    model = Site

    def get_queryset(self) -> QuerySet[Site]:
        qs = super().get_queryset()
        qs = qs.filter(
            created_by=self.request.user,
            deleted_at__isnull=True,
        )
        return qs


class DashboardView(UserPassesTestMixin, DetailView):
    """Display tracking info of a given site"""

    model = Site
    template_name = 'pixel/dashboard.html'

    def test_func(self):
        site: Site = self.get_object()
        return self.request.user == site.created_by


class SiteDetailApiView(LoginRequiredMixin, APIView):
    """Unregister a site"""

    def delete(self, request, pk, **kwargs):
        """Unregister a site"""
        site = get_object_or_404(Site, pk=pk)
        if request.user == site.created_by:
            site.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class DashboardBaseApiView(LoginRequiredMixin, APIView):
    """
    Base view to be used by all views
    that return data for chart rendering
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site = None
        self.pings = None

    @abstractmethod
    def process_data(self):
        pass

    def get(self, request, pk):
        """Get site, pings and process data"""
        self.site = get_object_or_404(Site, pk=pk)
        if self.request.user != self.site.created_by:
            return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)
        self.pings = self.site.get_pings(
            initial_datetime=self.request.query_params.get('start'),
            final_datetime=self.request.query_params.get('end'),
        )
        data = self.process_data()
        data['success'] = True
        return Response(data)


class DashboardGeneralInfoApiView(DashboardBaseApiView):
    """General info"""

    def process_data(self):
        """General aggregated info"""
        online_users = self.site.get_online_users()
        visitors = self.site.get_visitors(pings=self.pings)
        views = self.site.get_views(pings=self.pings)
        avg_duration = self.site.get_avg_duration(pings=self.pings).split('.')[0]
        bounce_rate = self.site.get_bounce_rate(pings=self.pings)
        return {
            'users': online_users.count(),
            'visitors': visitors.count(),
            'views': views.count(),
            'duration': avg_duration,
            'bounce': f"{bounce_rate:.0%}",
        }


class DashboardAggregatedByDateApiView(DashboardBaseApiView):
    """By date"""

    def process_data(self):
        """Info by date"""
        qs = self.pings.filter(
            event='pageload'
        ).annotate(
            date=TruncDay('timestamp')
        ).values('date')
        qs = qs.annotate(
            views=Count('id'),
            visitors=Count('user_id', distinct=True),
            duration=Avg('duration'),
        ).values('date', 'views', 'visitors', 'duration')
        data = []
        for item in qs:
            closed_sessions = self.pings.filter(
                timestamp__date=item['date'],
                event='pageload',
                duration__isnull=False,
            )
            if not closed_sessions.exists():
                item['bounce'] = None
            else:
                bounces = 0
                for user_id in self.pings.values_list('user_id', flat=True).distinct():
                    closed_sessions_count = (
                        closed_sessions
                        .filter(user_id=user_id)
                        .values('document_location')
                        .distinct()
                        .count()
                    )
                    bounces += 1 if closed_sessions_count == 1 else 0
                item['bounce'] = bounces / closed_sessions.count()
            data.append(item)
        return {'data': data}


class DashboardAggregatedByDocLocApiView(DashboardBaseApiView):
    """By document location"""

    def process_data(self):
        """Info by document location"""
        qs = self.pings.filter(
            event='pageload'
        ).values('document_location')
        qs = qs.annotate(
            views=Count('id'),
            visitors=Count('user_id', distinct=True),
            duration=Avg('duration'),
        ).values('document_location', 'views', 'visitors', 'duration')
        return {'data': list(qs)}
