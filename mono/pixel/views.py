from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
import base64
import pytz
import logging
from urllib.parse import urlparse

from .models import Ping, Site


PIXEL_GIF_DATA = base64.b64decode(
    b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


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
    tracking_info = get_tracking_info(request.GET)
    store_tracking_info(tracking_info)
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')


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
