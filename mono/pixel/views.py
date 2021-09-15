from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime, timedelta
import base64
import pytz
import logging
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


def get_tracking_info(query_dict):
    tracking_info = {
        'site_id': query_dict.get('id').replace('ID-', ''),
        'user_id': query_dict.get('uid'),
        'event': query_dict.get('ev'),
        'event_data': query_dict.get('ed'),
        'openpixel_js_version': query_dict.get('v'),
        'document_location': query_dict.get('dl'),
        'referrer_location': query_dict.get('rl'),
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
    try:
        Ping.objects.create(**tracking_info)
    except Site.DoesNotExist:
        logging.warning('Invalid ping')


@csrf_exempt
def pixel_gif(request):
    tracking_info = get_tracking_info(request.GET)
    store_tracking_info(tracking_info)
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
