import logging
from base64 import b64decode
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pytz
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDay
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.http.response import Http404, JsonResponse
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
from .mixins import PassRequestToFormViewMixin
from .models import Ping, Site


def get_timestamp(query_dict):
    if 'ts' in query_dict:
        EPOCH = datetime(1970, 1, 1, tzinfo=pytz.UTC)
        milliseconds = int(query_dict.get('ts'))
        return EPOCH + timedelta(milliseconds=milliseconds)
    else:
        return None


def get_implicit_domain_name_url(full_url):
    """
        Convert full absolute URL to implicit domain name
        Eg:
            https://developer.mozilla.org/en-US/docs/Learn -> /en-US/docs/Learn
    """
    parsed_uri = urlparse(full_url)
    return parsed_uri.netloc


def shorten_url(full_url: str, site_id: str):
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
    if Site.objects.filter(id=tracking_info.get('site_id')).exists():
        event = tracking_info['event']
        if event == 'pageclose':
            ping: Ping = Ping.objects.filter(
                site_id=tracking_info['site_id'],
                user_id=tracking_info['user_id'],
                document_location=tracking_info['document_location'],
            ).last()
            if ping is not None:
                ping.pageclose_timestamp = tracking_info['timestamp']
                ping.duration = tracking_info['timestamp'] - ping.pageload_timestamp
                ping.save()
        else:
            if tracking_info['event'] == 'pageload':
                tracking_info['pageload_timestamp'] = tracking_info['timestamp']
            ping = Ping.objects.create(**tracking_info)
    else:
        logging.warning('Invalid ping')


@csrf_exempt
def pixel_gif(request):
    if request.GET:
        tracking_info = get_tracking_info(request.GET)
        store_tracking_info(tracking_info)
    PIXEL_GIF_DATA = b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')


class RootView(RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            # TODO: redirect to an informational page
            return None
        qs = Site.objects.filter(created_by=self.request.user)
        if qs.exists():
            return reverse('pixel:dashboard', args=[qs.first().id])
        else:
            # TODO: redirect to site creation page
            return None


class SiteCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, CreateView):
    model = Site
    form_class = SiteForm
    success_url = reverse_lazy('pixel:tags')


class SitesView(LoginRequiredMixin, ListView):

    model = Site

    def get_queryset(self) -> QuerySet[Site]:
        qs = super().get_queryset()
        qs = qs.filter(
            created_by=self.request.user,
            deleted_at__isnull=True,
        )
        return qs


class DashboardView(UserPassesTestMixin, DetailView):

    model = Site
    template_name = 'pixel/dashboard.html'

    def test_func(self):
        site: Site = self.get_object()
        return self.request.user == site.created_by


class SiteDetailApiView(LoginRequiredMixin, APIView):

    def get_object(self, pk):
        try:
            return Site.objects.get(pk=pk)
        except Site.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None, **kwargs):
        site: Site = self.get_object(pk)
        if request.user == site.created_by:
            site.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class DashboardBaseApiView(LoginRequiredMixin, APIView):

    def get_object(self, pk):
        try:
            return Site.objects.get(pk=pk)
        except Site.DoesNotExist:
            raise Http404

    def process_data(self):
        return {}

    def get(self, request, pk, format=None):
        self.site: Site = self.get_object(pk)
        if self.request.user == self.site.created_by:
            self.pings = self.site.get_pings(
                initial_datetime=self.request.query_params.get('start'),
                final_datetime=self.request.query_params.get('end'),
            )
            data = self.process_data()
            data['success'] = True
            return Response(data)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class DashboardGeneralInfoApiView(DashboardBaseApiView):

    def process_data(self):
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
            'bounce': "{:.0%}".format(bounce_rate),
        }


class DashboardAggregatedByDateApiView(DashboardBaseApiView):

    def process_data(self):
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
                for v in self.pings.values('user_id').distinct():
                    c = closed_sessions.filter(user_id=v['user_id']).values('document_location').distinct().count()
                    if c == 1:
                        bounces += 1
                item['bounce'] = bounces / closed_sessions.count()
            data.append(item)
        return {'data': data}


class DashboardAggregatedByDocLocApiView(DashboardBaseApiView):

    def process_data(self):
        qs = self.pings.filter(
            event='pageload'
        ).values('document_location')
        qs = qs.annotate(
            views=Count('id'),
            visitors=Count('user_id', distinct=True),
            duration=Avg('duration'),
        ).values('document_location', 'views', 'visitors', 'duration')
        return {'data': list(qs)}


@user_passes_test(lambda user: user.is_authenticated)
def test(request):

    site: Site = Site.objects.get(id='b022642e-219d-43e8-a833-da2f73c1e255')

    initial_datetime = datetime(2021, 9, 16, tzinfo=pytz.UTC)
    # final_datetime = datetime(2021, 9, 17)

    pings = site.get_pings(
        initial_datetime=initial_datetime,
    )
    visitors = site.get_visitors(pings=pings)
    views = site.get_views(pings=pings)
    avg_duration = site.get_avg_duration(pings=pings)

    # Dimensions
    document_locations = site.get_document_locations(pings=pings)
    referrer_locations = site.get_referrer_locations(pings=pings)
    browsers = site.get_browsers(pings=pings)

    views_by_document_location = document_locations.annotate(views=Count('id', filter=Q(event='pageload')))
    views_by_referrer_location = referrer_locations.annotate(views=Count('id', filter=Q(event='pageload')))
    views_by_browser = browsers.annotate(views=Count('id', filter=Q(event='pageload')))

    visitors_by_document_location = document_locations.annotate(visitors=Count('user_id', distinct=True, filter=Q(event='pageload')))
    visitors_by_referrer_location = referrer_locations.annotate(visitors=Count('user_id', distinct=True, filter=Q(event='pageload')))
    visitors_by_browser = browsers.annotate(visitors=Count('user_id', distinct=True, filter=Q(event='pageload')))

    resp = {}
    resp['pings'] = pings.count()
    resp['visitors'] = visitors.count()
    resp['views'] = views.count()
    resp['avg_duration'] = avg_duration
    resp['views_by_document_location'] = list(views_by_document_location)
    resp['views_by_referrer_location'] = list(views_by_referrer_location)
    resp['views_by_browser'] = list(views_by_browser)
    resp['visitors_by_document_location'] = list(visitors_by_document_location)
    resp['visitors_by_referrer_location'] = list(visitors_by_referrer_location)
    resp['visitors_by_browser'] = list(visitors_by_browser)
    return JsonResponse(resp)
