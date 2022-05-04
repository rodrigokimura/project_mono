"""Useful context processors"""
from collections import namedtuple

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def environment(request):
    return {'APP_ENV': settings.APP_ENV}


def language_extras(request):
    """Extra language settings for the template context"""
    tinymce_languages = {
        'pt-br': 'pt_BR'
    }
    tinymce_language = tinymce_languages.get(request.LANGUAGE_CODE)
    return {
        'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        'tinymce_language': tinymce_language
    }


def apps_menu(request):
    """Apps menu for the template context"""
    AppInfo = namedtuple('AppInfo', ['name', 'url', 'emoji', 'secret'])
    apps = [
        AppInfo('Finance', '/fn/', 'dollar', False),
        AppInfo('Project Manager', '/pm/', 'dividers', False),
        AppInfo('Notes', '/nt/', 'notepad_spiral', False),
        AppInfo('Checklists', '/cl/', 'ballot_box_with_check', False),
        AppInfo('Pixel', '/pixel/', 'bar_chart', False),
        AppInfo('Shipper', '/shipper/', 'couple_with_heart', False),
        AppInfo('Coder', '/cd/', 'card_box', False),
    ]
    if request.user.is_superuser:
        apps += [
            AppInfo('Curriculum builder', '/cb/', 'bookmark_tabs', True),
            AppInfo('Admin', '/admin/', 'control_knobs', True),
            AppInfo('Restricted Area', '/restricted-area/', 'closed_lock_with_key', True),
            AppInfo('Watcher', '/watcher/', 'pager', True),
            AppInfo('Healthcheck', '/hc/home/', 'thermometer', True),
        ]
    return {
        'apps_menu': apps
    }
